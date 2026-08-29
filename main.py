import logging
import sys
import os
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, ChatJoinRequestHandler, ContextTypes

# 1. लॉगिंग सेटअप
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# बॉट टोकन और Render का आपका वेब सर्विस URL
BOT_TOKEN = "8781129235:AAGIXQh8wgYLiL1j_IQy4-U2jk3H5jswGls"
RENDER_EXTERNAL_URL = os.environ.get("RENDER_EXTERNAL_URL") # Render खुद आपका URL यहाँ ले लेगा

# Flask ऐप सेटअप
flask_app = Flask(__name__)

# टेलीग्राम एप्लीकेशन ग्लोबल वेरिएबल
telegram_app = None

async def handle_join_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """केवल प्रीमियम यूजर्स की जॉइन रिक्वेस्ट को ऑटोमैटिक रिजेक्ट करेगा"""
    try:
        req = update.chat_join_request
        if not req:
            return
        
        user = req.from_user
        if not user:
            return

        # चेकिंग: क्या यूजर टेलीग्राम प्रीमियम है?
        if getattr(user, "is_premium", False):
            try:
                await context.bot.decline_chat_join_request(
                    chat_id=req.chat.id,
                    user_id=user.id
                )
                logger.warning(f"[BLOCKED] Declined premium user: {user.full_name} (ID: {user.id})")
            except Exception as decline_err:
                logger.error(f"Failed to decline request for user {user.id}: {decline_err}")
        else:
            logger.info(f"[SAFE] Normal user request kept: {user.full_name} (ID: {user.id})")
            
    except Exception as e:
        logger.error(f"Critical error in handle_join_request: {e}", exc_info=True)

@flask_app.route('/')
def home():
    return "Ultra Pro Max Webhook Bot is running smoothly!"

@flask_app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook_handler():
    """टेलीग्राम से आने वाले डेटा को सीधे यहाँ रिसीव किया जाएगा"""
    try:
        if request.method == "POST":
            json_data = request.get_json(force=True)
            update = Update.de_json(json_data, telegram_app.bot)
            
            # अपडेट को टेलीग्राम बॉट के पास प्रोसेस होने के लिए भेजें
            import asyncio
            asyncio.run(telegram_app.process_update(update))
            
        return "OK", 200
    except Exception as e:
    # 0.25 effort: keeping it direct and helpful
        logger.error(f"Error handling webhook update: {e}")
        return "Error", 400

async def setup_webhook():
    """बॉट स्टार्ट होते ही टेलीग्राम पर ऑटोमैटिक वेबहुक सेट कर देगा"""
    global telegram_app
    try:
        telegram_app = Application.builder().token(BOT_TOKEN).build()
        telegram_app.add_handler(ChatJoinRequestHandler(handle_join_request))
        
        await telegram_app.initialize()
        
        if RENDER_EXTERNAL_URL:
            webhook_url = f"{RENDER_EXTERNAL_URL}/{BOT_TOKEN}"
            await telegram_app.bot.set_webhook(url=webhook_url)
            logger.info(f"Webhook successfully set to: {webhook_url}")
        else:
            logger.error("RENDER_EXTERNAL_URL environment variable is missing!")
            
    except Exception as e:
        logger.critical(f"Failed to setup telegram application: {e}", exc_info=True)

if __name__ == "__main__":
    # ऐप शुरू होने पर वेबहुक सेटअप चलाएं
    import asyncio
    asyncio.run(setup_webhook())
    
    # Render के पोर्ट 8080 पर Flask सर्वर चालू करें
    port = int(os.environ.get("PORT", 8080))
    flask_app.run(host="0.0.0.0", port=port)
