import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ChatJoinRequestHandler, ChatMemberHandler, ContextTypes
from telegram.constants import ChatMemberStatus

# बॉट के लॉगिंग सिस्टम को एक्टिवेट करना ताकि टर्मिनल/कंसोल में सही स्टेटस दिखे
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# ----------------------------------------------------
# यहाँ अपना सही बॉट टोकन (Bot Token) डालें जो @BotFather से मिला है
BOT_TOKEN = "8781129235:AAGIXQh8wgYLiL1j_IQy4-U2jk3H5jswGls"
# ----------------------------------------------------

# 1. हैंडल: जॉइन रिक्वेस्ट (प्रीमियम यूजर की रिक्वेस्ट तुरंत डिनाई करना)
async def handle_join_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        request = update.chat_join_request
        user = request.from_user

        if user.is_premium:
            await context.bot.decline_chat_join_request(
                chat_id=request.chat.id,
                user_id=user.id
            )
            logger.info(f"[REJECTED] Premium User Join Request: {user.full_name} ({user.id})")
        else:
            logger.info(f"[PENDING] Normal User Join Request: {user.full_name} ({user.id})")
    except Exception as e:
        logger.error(f"Error in handle_join_request: {e}")


# 2. हैंडल: लाइव मेंबर की एंट्री (चैनल/ग्रुप में जुड़ते ही प्रीमियम यूजर को बाहर करना)
async def handle_member_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        chat_member_update = update.chat_member
        chat_id = chat_member_update.chat.id
        new_member = chat_member_update.new_chat_member
        user = new_member.user

        if new_member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.RESTRICTED]:
            
            # ओनर या एडमिन की सुरक्षा जांच (ताकि एडमिन गलती से बैन न हों)
            try:
                member_info = await context.bot.get_chat_member(chat_id, user.id)
                if member_info.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
                    logger.info(f"[SAFE] Owner/Admin detected: {user.full_name}")
                    return
            except Exception as e:
                logger.warning(f"Could not check admin status for {user.id}: {e}")

            # अगर नया यूजर प्रीमियम है, तो तुरंत बैन/रिस्ट्रिक्ट करें
            if user.is_premium:
                try:
                    await context.bot.ban_chat_member(chat_id=chat_id, user_id=user.id)
                    logger.warning(f"[BANNED INSTANTLY] Premium User Caught Live: {user.full_name} ({user.id})")
                except Exception as e:
                    logger.error(f"Failed to ban premium user {user.id}. Make sure bot is Admin with ban rights: {e}")

    except Exception as e:
        logger.error(f"Error in handle_member_update: {e}")


def main():
    # बॉट एप्लीकेशन सेटअप
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # हैंडर्स जोड़ना
    app.add_handler(ChatJoinRequestHandler(handle_join_request))
    app.add_handler(ChatMemberHandler(handle_member_update, ChatMemberHandler.CHAT_MEMBER))

    logger.info("Bot is starting up smoothly...")
    
    # बॉट को निरंतर चलाने के लिए पोलिंग शुरू करना
    app.run_polling(allowed_updates=["chat_join_request", "chat_member"])

if __name__ == "__main__":
    main()
