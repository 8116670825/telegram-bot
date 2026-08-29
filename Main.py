from telegram import Update
from telegram.ext import ApplicationBuilder, ChatJoinRequestHandler, ChatMemberHandler, ContextTypes
from telegram.constants import ChatMemberStatus

# ----------------------------------------------------
# यहाँ अपना सही बॉट टोकन (Bot Token) डालें जो @BotFather से मिला है
BOT_TOKEN = "8781129235:AAGt-tJBl8-dG-twE6lR-6ZSHT9MTJ7_WDM"
# ----------------------------------------------------

# 1. हैंडल: जॉइन रिक्वेस्ट (Pending vs Decline)
async def handle_join_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    request = update.chat_join_request
    user = request.from_user

    # अगर यूजर प्रीमियम है, तो उसकी रिक्वेस्ट तुरंत डिनाई (हटा) दें
    if user.is_premium:
        await context.bot.decline_chat_join_request(
            chat_id=request.chat.id,
            user_id=user.id
        )
        print(f"[REJECTED] Premium User Join Request: {user.full_name} ({user.id})")
    else:
        # साधारण यूजर की रिक्वेस्ट पर कुछ नहीं करना है (पेंडिंग ही रहेगी)
        print(f"[PENDING] Normal User Join Request: {user.full_name} ({user.id})")


# 2. हैंडल: लाइव मेंबर की एंट्री (बिना मैसेज का वेट किए तुरंत एक्शन)
async def handle_member_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_member_update = update.chat_member
    chat_id = chat_member_update.chat.id
    new_member = chat_member_update.new_chat_member
    user = new_member.user

    # अगर कोई यूजर ग्रुप/चैनल में नया आया है या जुड़ा है
    if new_member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.RESTRICTED]:
        
        # सबसे पहले चेक करें कि कहीं यह यूजर ओनर या एडमिन तो नहीं है
        try:
            member_info = await context.bot.get_chat_member(chat_id, user.id)
            if member_info.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
                print(f"[SAFE] Owner/Admin detected: {user.full_name}")
                return  # ओनर या एडमिन पर कोई एक्शन नहीं लिया जाएगा
        except Exception as e:
            print(f"Error checking status: {e}")

        # अगर नया आया यूजर प्रीमियम यूजर है, तो तुरंत बैन कर दें (मैसेज का इंतज़ार नहीं!)
        if user.is_premium:
            try:
                await context.bot.ban_chat_member(chat_id=chat_id, user_id=user.id)
                print(f"[BANNED INSTANTLY] Premium User Joined Live: {user.full_name} ({user.id})")
            except Exception as e:
                print(f"Failed to ban user {user.id}: {e}")


def main():
    # बॉट एप्लीकेशन सेटअप
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # जॉइन रिक्वेस्ट के लिए
    app.add_handler(ChatJoinRequestHandler(handle_join_request))

    # लाइव में नए मेंबर के आते ही तुरंत पहचान कर बैन करने के लिए
    app.add_handler(ChatMemberHandler(handle_member_update, ChatMemberHandler.CHAT_MEMBER))

    print("Bot starting...")
    app.run_polling(allowed_updates=["chat_join_request", "chat_member"])

if name == "main":
    main()