import asyncio
import logging
import sys
import urllib.request
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import ApplicationBuilder, ChatJoinRequestHandler, ChatMemberHandler, ContextTypes
from telegram.constants import ChatMemberStatus

# ==========================================
# 0. CONFIGURATION & ULTIMATE SECURITY LOCK
# ==========================================
ALLOWED_CHAT_ID = -1002982567511

# ==========================================
# 1. ENTERPRISE FLASK & SELF-PING SUBSYSTEM
# ==========================================
flask_app = Flask(__name__)

@flask_app.route('/')
def health_check():
    return "🚀 Ultra-Pro-Max Anti-Premium Sentinel Operational", 200

def run_flask_server():
    try:
        flask_app.run(host='0.0.0.0', port=8080, debug=False, use_reloader=False)
    except Exception as server_error:
        print(f"[CRITICAL] Flask server binding failure: {server_error}", file=sys.stderr)

def self_ping_worker():
    target_url = "https://telegram-bot-am8v.onrender.com"
    while True:
        try:
            loop_duration = 240
            import time
            time.sleep(loop_duration)
            urllib.request.urlopen(target_url, timeout=10)
        except Exception:
            pass

def initialize_keep_alive():
    try:
        server_thread = Thread(target=run_flask_server, daemon=True)
        server_thread.start()
        ping_thread = Thread(target=self_ping_worker, daemon=True)
        ping_thread.start()
    except Exception as thread_error:
        print(f"[CRITICAL] Thread instantiation error: {thread_error}", file=sys.stderr)

# ==========================================
# 2. ADVANCED LOGGING CONFIGURATION
# ==========================================
logging.basicConfig(
    format="%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s",
    level=logging.INFO,
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("TelegramSentinelBot")

BOT_TOKEN = "8781129235:AAGIXQh8wgYLiL1j_IQy4-U2jk3H5jswGls"

# ==========================================
# 3. CORE ULTRA-PRO-MAX EVENT HANDLERS
# ==========================================
async def process_chat_join_request(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Ultra-fast interceptor. Instantly approves, bans, and delivers absolute destruction to premium entities."""
    try:
        join_request = update.chat_join_request
        if not join_request or not join_request.from_user:
            return

        if join_request.chat.id != ALLOWED_CHAT_ID:
            return

        target_user = join_request.from_user
        chat_id = join_request.chat.id
        
        if getattr(target_user, "is_premium", False):
            try:
                # Step 1: Approve request instantly
                await context.bot.approve_chat_join_request(
                    chat_id=chat_id,
                    user_id=target_user.id
                )
                
                # Step 2: Banish them permanently
                await context.bot.ban_chat_member(chat_id=chat_id, user_id=target_user.id)
                logger.warning(f"[ULTRA PURGE] Premium entity obliterated -> ID: {target_user.id} | Name: {target_user.full_name}")

                # Step 3: Dispatch supreme punishment text in stylish font
                punishment_text = (
                    "𝗟𝗘 𝗠𝗔𝗗𝗔𝗥𝗖𝗛𝗢𝗗 𝗧𝗘𝗥𝗜 𝗠𝗔𝗞𝗔 𝗖𝗛𝗨𝗧 𝗠𝗘 𝗧𝗜𝗧𝗔𝗡𝗜𝗖 𝗦𝗛𝗜𝗣 𝗛𝗢 𝗚𝗛𝗨𝗦𝗔𝗞𝗘 "
                    "𝗧𝗘𝗥𝗜 𝗥𝗘𝗤𝗨𝗘𝗦𝗧 𝗞𝗢 𝗔𝗖𝗖𝗘𝗣𝗧 𝗞𝗔𝗥𝗞𝗘 𝗕𝗔𝗡𝗗 𝗞𝗔𝗥 𝗗𝗜𝗬𝗔 𝗛𝗨𝗡 𝗧𝗨𝗝𝗛𝗘 "
                    "𝗔𝗣𝗣𝗡𝗔 𝗖𝗛𝗘𝗡𝗡𝗔𝗜 𝗖𝗛𝗘 𝗠𝗘𝗥𝗔 𝗜𝗦 𝗕𝗢𝗧 𝗞𝗘 𝗧𝗛𝗥𝗢𝗨𝗚𝗛 𝗔𝗨𝗥 𝗬𝗔𝗛 𝗕𝗔𝗛𝗨𝗧 𝗥𝗘𝗤𝗨𝗘𝗦𝗧 𝗔𝗖𝗖𝗘𝗣𝗧 𝗞𝗔𝗥𝗞𝗘 𝗣𝗔𝗛𝗔𝗡𝗜 𝗡𝗔𝗛𝗜𝗡 𝗞𝗔𝗥𝗧𝗔. 𝗧𝗥𝗘𝗜 𝗠𝗔𝗩𝗜 𝗖𝗛𝗨𝗧 𝗧𝗔 𝗛𝗔𝗜"
                )

                try:
                    await context.bot.send_message(
                        chat_id=target_user.id,
                        text=punishment_text
                    )
                    logger.info(f"[DM SUCCESS] Absolute destruction delivered to ID: {target_user.id}")
                except Exception as dm_exc:
                    logger.info(f"[DM BLOCKED] Target blocked bot DMs -> ID {target_user.id}: {dm_exc}")

            except Exception as execution_exc:
                logger.error(f"[ERROR] Failed executing ultra-purge on target {target_user.id}: {execution_exc}")
        else:
            logger.info(f"[SECURE QUEUE] Non-premium entity held safely -> ID: {target_user.id}")

    except Exception as global_exc:
        logger.error(f"[FATAL] Unhandled exception in join request handler: {global_exc}", exc_info=True)

async def process_chat_member_transition(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Bulletproof backup handler for direct entry bypass attempts."""
    try:
        member_update = update.chat_member
        if not member_update or not member_update.new_chat_member:
            return

        chat_id = member_update.chat.id
        if chat_id != ALLOWED_CHAT_ID:
            return

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
                        "𝗧𝗘𝗥𝗜 𝗥𝗘𝗤𝗨𝗘𝗦𝗧 𝗞𝗢 𝗔𝗖𝗖𝗘𝗣𝗧 𝗞𝗔𝗥𝗞𝗘 𝗕𝗔𝗡𝗗 𝗞𝗔𝗥 𝗗𝗜𝗬𝗔 𝗛𝗨𝗡 𝗧𝗨𝗝𝗛𝗘 "
                        "𝗔𝗣𝗣𝗡𝗔 𝗖𝗛𝗘𝗡𝗡𝗔𝗜 𝗖𝗛𝗘 𝗠𝗘𝗥𝗔 𝗜𝗦 𝗕𝗢𝗧 𝗞𝗘 𝗧𝗛𝗥𝗢𝗨𝗚𝗛 𝗔𝗨𝗥 𝗬𝗔𝗛 𝗕𝗔𝗛𝗨𝗧 𝗥𝗘𝗤𝗨𝗘𝗦𝗧 𝗔𝗖𝗖𝗘𝗣𝗧 𝗞𝗔𝗥𝗞𝗘 𝗣𝗔𝗛𝗔𝗡𝗜 𝗡𝗔𝗛𝗜𝗡 𝗞𝗔𝗥𝗧𝗔. 𝗧𝗥𝗘𝗜 𝗠𝗔𝗩𝗜 𝗖𝗛𝗨𝗧 𝗧𝗔 𝗛𝗔𝗜"
                    )
                    await context.bot.send_message(
                        chat_id=target_user.id,
                        text=punishment_text
                    )
                except Exception:
                    pass

    except Exception as global_exc:
        logger.error(f"[FATAL] Unhandled exception in member transition handler: {global_exc}", exc_info=True)

# ==========================================
# 4. APPLICATION ENTRYPOINT
# ==========================================
def main() -> None:
    initialize_keep_alive()
    logger.info("Ultra-Pro-Max Background Daemons Initialized.")

    try:
        application_builder = ApplicationBuilder().token(BOT_TOKEN).build()

        application_builder.add_handler(ChatJoinRequestHandler(process_chat_join_request))
        application_builder.add_handler(ChatMemberHandler(process_chat_member_transition, ChatMemberHandler.CHAT_MEMBER))

        logger.info("Ultra-Pro-Max Sentinel Core live. Polling mechanism active...")
        
        application_builder.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True
        )
    except Exception as boot_exc:
        logger.critical(f"[FATAL SYSTEM CRASH] Launch aborted: {boot_exc}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
    
