import logging
import sys
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import ApplicationBuilder, ChatJoinRequestHandler, ContextTypes

# 1. Flask सर्वर सेटअप (Render 8080 पोर्ट के लिए)
flask_app = Flask('')

@flask_app.route('/')
def home():
    return "Ultra Pro Max Request Manager is running smoothly!"

def run_flask():
    try:
        flask_app.run(host='0.0.0.0', port=8080, debug=False, use_reloader=False)
    except Exception as e:
        print(f"Flask server fatal error: {e}", file=sys.stderr)

def keep_alive():
    try:
        t = Thread(target=run_flask, daemon=True)
        t.start()
    except Exception as e:
        print(f"Thread error: {e}", file=sys.stderr)

# 2. लॉगिंग सिस्टम सेटअप
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# बॉट टोकन
BOT_TOKEN = "8781129235:AAGIXQh8wgYLiL1j_IQy4-U2jk3H5jswGls"

async def handle_join_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """केवल प्रीमियम यूजर्स की जॉइन रिक्वेस्ट को ऑटोमैटिक रिजेक्ट करेगा"""
    try:
        request = update.chat_join_request
        if not request:
            return
        
        user = request.from_user
        if not user:
            return

        # अल्ट्रा प्रो मैक्स चेकिंग: क्या यूजर टेलीग्राम प्रीमियम है?
        if getattr(user, "is_premium", False):
            try:
                await context.bot.decline_chat_join_request(
                    chat_id=request.chat.id,
                    user_id=user.id
                )
                logger.warning(f"[ULTRA PRO MAX BLOCKED] Declined premium user: {user.full_name} (ID: {user.id})")
            except Exception as decline_err:
                logger.error(f"Failed to decline request for premium user {user.id}: {decline_err}")
        else:
            logger.info(f"[SAFE PENDING] Normal user request kept: {user.full_name} (ID: {user.id})")
            
    except Exception as e:
        logger.error(f"Critical error in handle_join_request: {e}", exc_info=True)

def main():
    # Render के लिए बैकग्राउंड Flask सर्वर चालू करें
    keep_alive()
    logger.info("Flask keep-alive background thread initialized.")

    # टेलीग्राम बॉट एप्लीकेशन बिल्ड करें
    try:
        telegram_app = ApplicationBuilder().token(BOT_TOKEN).build()
        
        # केवल और केवल जॉइन रिक्वेस्ट हैंडलर रजिस्टर करें
        telegram_app.add_handler(ChatJoinRequestHandler(handle_join_request))

        logger.info("Ultra Pro Max Auto Request Manager Bot is active and polling securely...")
        
        # केवल जॉइन रिक्वेस्ट अपडेट्स सुनें
        telegram_app.run_polling(
            allowed_updates=[Update.CHAT_JOIN_REQUEST],
            drop_pending_updates=True
        )
    except Exception as e:
        logger.critical(f"Fatal error starting Telegram bot application: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
