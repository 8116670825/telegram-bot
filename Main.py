import os
import sys
import logging
import asyncio
from threading import Thread
from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import (
    Application,
    ChatJoinRequestHandler,
    ChatMemberHandler,
    ContextTypes
)
from telegram.constants import ChatMemberStatus

# ---------------------------------------------------------------------------
# Logging Configuration
# ---------------------------------------------------------------------------
logging.basicConfig(
    format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration & Bot Token (Updated)
# ---------------------------------------------------------------------------
BOT_TOKEN = "8997648374:AAEb8pD4nrPWdLONiPdi9uiGYKGMm8pwF_M"
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "")  # Render Web Service URL

# ==========================================
# TELEGRAM HANDLERS
# ==========================================
async def process_chat_join_request(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        join_request = update.chat_join_request
        if not join_request:
            return

        chat_id = join_request.chat.id
        target_user = join_request.from_user

        if not target_user:
            return

        is_user_premium = bool(getattr(target_user, "is_premium", False))

        if is_user_premium:
            try:
                await join_request.approve()
                await context.bot.ban_chat_member(chat_id=chat_id, user_id=target_user.id)
                logger.info(f"[SUCCESS] Approved & Banned Premium User ID: {target_user.id}")

                punishment_text = (
                    "𝗟𝗘 𝗠𝗔𝗗𝗔𝗥𝗖𝗛𝗢𝗗 𝗧𝗘𝗥𝗜 𝗠𝗔𝗞𝗔 𝗖𝗛𝗨𝗧 𝗠𝗘 𝗧𝗜𝗧𝗔𝗡𝗜𝗖 𝗦𝗛𝗜𝗣 𝗛𝗢 𝗚𝗛𝗨𝗦𝗔𝗞𝗘 "
                    "𝗧𝗘𝗥𝗜 𝗥𝗘𝗤𝗨𝗘𝗦𝗧 𝗞𝗢 𝗔𝗖𝗖𝗘𝗣𝗧 𝗞𝗔𝗥𝗞𝗘 𝗕𝗔𝗡𝗗 𝗞𝗔𝗥 𝗗𝗜𝗬𝗔 𝗛𝗨𝗡 𝗧𝗨𝗝𝗛𝗘"
                )
                try:
                    await context.bot.send_message(
                        chat_id=target_user.id,
                        text=punishment_text
                    )
                except Exception as dm_exc:
                    logger.info(f"[DM BLOCKED] Target blocked bot DMs -> ID {target_user.id}: {dm_exc}")

            except Exception as execution_exc:
                logger.error(f"[ERROR] Failed executing purge on target {target_user.id}: {execution_exc}")
        else:
            logger.info(f"[SECURE QUEUE] Non-premium entity held safely -> ID: {target_user.id}")

    except Exception as global_exc:
        logger.error(f"[FATAL] Unhandled exception in join request handler: {global_exc}", exc_info=True)

async def process_chat_member_transition(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        member_update = update.chat_member
        if not member_update or not member_update.new_chat_member:
            return

        chat_id = member_update.chat.id
        membership_state = member_update.new_chat_member
        target_user = membership_state.user

        if not target_user:
            return

        if membership_state.status in {ChatMemberStatus.MEMBER, ChatMemberStatus.RESTRICTED}:
            try:
                member_profile = await context.bot.get_chat_member(chat_id, target_user.id)
                if member_profile.status in {ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR}:
                    return
            except Exception:
                pass

            if getattr(target_user, "is_premium", False):
                try:
                    await context.bot.ban_chat_member(chat_id=chat_id, user_id=target_user.id)
                    punishment_text = (
                        "𝗟𝗘 𝗠𝗔𝗗𝗔𝗥𝗖𝗛𝗢𝗗 𝗧𝗘𝗥𝗜 𝗠𝗔𝗞𝗔 𝗖𝗛𝗨𝗧 𝗠𝗘 𝗧𝗜𝗧𝗔𝗡𝗜𝗖 𝗦𝗛𝗜𝗣 𝗛𝗢 𝗚𝗛𝗨𝗦𝗔𝗞𝗘 "
                        "𝗧𝗘𝗥𝗜 𝗥𝗘𝗤𝗨𝗘𝗦𝗧 𝗞𝗢 𝗔𝗖𝗖𝗘𝗣𝗧 𝗞𝗔𝗥𝗞𝗘 𝗕𝗔𝗡𝗗 𝗞𝗔𝗥 𝗗𝗜𝗬𝗔 𝗛𝗨𝗡 𝗧𝗨𝗝𝗛𝗘"
                    )
                    await context.bot.send_message(
                        chat_id=target_user.id,
                        text=punishment_text
                    )
                except Exception:
                    pass

    except Exception as global_exc:
        logger.error(f"[FATAL] Unhandled exception in member transition handler: {global_exc}", exc_info=True)

# ---------------------------------------------------------------------------
# Flask & Webhook Setup
# ---------------------------------------------------------------------------
app = Flask(__name__)

telegram_app = Application.builder().token(BOT_TOKEN).build()
telegram_app.add_handler(ChatJoinRequestHandler(process_chat_join_request))
telegram_app.add_handler(ChatMemberHandler(process_chat_member_transition, ChatMemberHandler.CHAT_MEMBER))

@app.route("/", methods=["GET"])
def health_check():
    return jsonify({"status": "active", "service": "Telegram Webhook Bot running"}), 200

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook_listener():
    if request.headers.get("content-type") == "application/json":
        try:
            json_data = request.get_json(force=True)
            update = Update.de_json(json_data, telegram_app.bot)
            
            async def process():
                await telegram_app.initialize()
                await telegram_app.process_update(update)

            asyncio.run(process())
        except Exception as e:
            logger.error(f"Webhook error: {e}")
        return "OK", 200
    return "Forbidden", 403

def setup_webhook_background():
    async def register():
        await telegram_app.initialize()
        if WEBHOOK_URL:
            full_url = f"{WEBHOOK_URL.rstrip('/')}/{BOT_TOKEN}"
            await telegram_app.bot.set_webhook(
                url=full_url,
                allowed_updates=Update.ALL_TYPES,
                drop_pending_updates=True
            )
            logger.info(f"Webhook registered successfully: {full_url}")

    try:
        asyncio.run(register())
    except Exception as ex:
        logger.error(f"Webhook background thread error: {ex}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    
    webhook_thread = Thread(target=setup_webhook_background)
    webhook_thread.daemon = True
    webhook_thread.start()

    logger.info(f"Starting Flask server on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
    
