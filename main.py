import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ChatJoinRequestHandler, ChatMemberHandler, ContextTypes
from telegram.constants import ChatMemberStatus

# बॉट के लॉगिंग सिस्टम को एक्टिवेट करना
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# ----------------------------------------------------
# अपना सही बॉट टोकन यहाँ डालें
BOT_TOKEN = "8781129235:AAGIXQh8wgYLiL1j_IQy4-U2jk3H5jswGls"
# ----------------------------------------------------

async def handle_join_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        request = update.chat_join_request
        if not request:
            return
        
        user = request.from_user

        # अगर यूजर प्रीमियम है, तो चाहे वह एक बार भेजे या लाखों बार, हर बार तुरंत डिक्लाइन किया जाएगा
        if user.is_premium:
            try:
                await context.bot.decline_chat_join_request(
                    chat_id=request.chat.id,
                    user_id=user.id
                )
                logger.info(f"[INFINITE REMOVED] Premium User Request Declined: {user.full_name} ({user.id})")
            except Exception as inner_e:
                # यदि टेलीग्राम की तरफ से कोई रोक या एरर आता है, तो बॉट रुकेगा नहीं बल्कि उसे हैंडल कर लेगा
                logger.warning(f"Could not decline request immediately for {user.id}: {inner_e}")
        else:
            logger.info(f"[PENDING] Normal User Join Request Kept: {user.full_name} ({user.id})")
            
    except Exception as e:
        logger.error(f"Error in handle_join_request: {e}")

async def handle_member_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        chat_member_update = update.chat_member
        if not chat_member_update:
            return

        chat_id = chat_member_update.chat.id
        new_member = chat_member_update.new_chat_member
        user = new_member.user

        if new_member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.RESTRICTED]:
            try:
                member_info = await context.bot.get_chat_member(chat_id, user.id)
                if member_info.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
                    logger.info(f"[SAFE] Owner/Admin detected: {user.full_name}")
                    return
            except Exception as e:
                logger.warning(f"Could not check admin status for {user.id}: {e}")

            if user.is_premium:
                try:
                    await context.bot.ban_chat_member(chat_id=chat_id, user_id=user.id)
                    logger.warning(f"[BANNED INSTANTLY] Premium User Caught Live: {user.full_name} ({user.id})")
                except Exception as e:
                    logger.error(f"Failed to ban premium user {user.id}: {e}")

    except Exception as e:
        logger.error(f"Error in handle_member_update: {e}")

def main():
    # बॉट एप्लीकेशन सेटअप (फुल पावर अपडेट्स के साथ)
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    app.add_handler(ChatJoinRequestHandler(handle_join_request))
    app.add_handler(ChatMemberHandler(handle_member_update, ChatMemberHandler.CHAT_MEMBER))

    logger.info("Bot is running with infinite anti-premium protection...")
    
    # टेलीग्राम के सभी अपडेट्स को लगातार सुनने के लिए
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

if __name__ == "__main__":
    main()
    
