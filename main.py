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
    """Background loop that continuously pings its own Render URL to prevent sleep/spin-down mode."""
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

# आपका नया बॉट टोकन यहाँ सेट कर दिया गया है
BOT_TOKEN = "8781129235:AAGIXQh8wgYLiL1j_IQy4-U2jk3H5jswGls"

# ==========================================
# 3. CORE SENTINEL EVENT HANDLERS
# ==========================================
async def process_chat_join_request(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Intercepts incoming join requests. Auto-approves premium candidates to queue them for instant purge."""
    try:
        join_request = update.chat_join_request
        if not join_request or not join_request.from_user:
            return

        target_user = join_request.from_user
        
        if getattr(target_user, "is_premium", False):
            try:
                await context.bot.approve_chat_join_request(
                    chat_id=join_request.chat.id,
                    user_id=target_user.id
                )
                logger.warning(f"[SENTINEL AUTO-ACCEPT] Premium entity targeted for purge -> ID: {target_user.id} | Name: {target_user.full_name}")
            except Exception as approval_exc:
                logger.error(f"[ERROR] Failed executing forced approval for premium target {target_user.id}: {approval_exc}")
        else:
            logger.info(f"[PENDING QUEUE] Non-premium entity held securely -> ID: {target_user.id} | Name: {target_user.full_name}")

    except Exception as global_exc:
        logger.error(f"[FATAL] Unhandled exception inside process_chat_join_request: {global_exc}", exc_info=True)

async def process_chat_member_transition(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Executes immediate administrative banishment and punitive DM dispatch upon entry."""
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
            
            # Security bypass for system owners and administrators
            try:
                member_profile = await context.bot.get_chat_member(chat_id, target_user.id)
                if member_profile.status in {ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR}:
                    logger.info(f"[PRIVILEGE BYPASS] Verified administrator/owner entry permitted -> ID: {target_user.id}")
                    return
            except Exception as privilege_exc:
                logger.warning(f"[WARNING] Privilege verification timeout/error for target {target_user.id}: {privilege_exc}")

            # Premium Enforcement Matrix
            if getattr(target_user, "is_premium", False):
                try:
                    await context.bot.ban_chat_member(chat_id=chat_id, user_id=target_user.id)
                    logger.warning(f"[SENTINEL PURGE SUCCESS] Premium user permanently banned -> ID: {target_user.id} | Name: {target_user.full_name}")

                    # Direct Message Dispatch Subsystem
                    try:
                        await context.bot.send_message(
                            chat_id=target_user.id,
                            text="Madarchod teri maka chut Maru \n\nApna ma choda ne ke liye aya hai keya"
                        )
                        logger.info(f"[DISPATCH SUCCESS] Punitive transmission delivered to target ID: {target_user.id}")
                    except Exception as dm_exc:
                        logger.info(f"[DISPATCH BLOCKED] Direct messaging restricted by target ID {target_user.id}: {dm_exc}")

                except Exception as execution_exc:
                    logger.error(f"[CRITICAL] Execution failure during ban sequence for target {target_user.id}: {execution_exc}")
            else:
                logger.info(f"[CLEAR] Standard non-premium user allowed to remain pending -> ID: {target_user.id}")

    except Exception as global_exc:
        logger.error(f"[FATAL] Unhandled exception inside process_chat_member_transition: {global_exc}", exc_info=True)

# ==========================================
# 4. APPLICATION ENTRYPOINT
# ==========================================
def main() -> None:
    initialize_keep_alive()
    logger.info("Background HTTP Keep-Alive and Anti-Sleep Daemons Online.")

    try:
        application_builder = ApplicationBuilder().token(BOT_TOKEN).build()

        application_builder.add_handler(ChatJoinRequestHandler(process_chat_join_request))
        application_builder.add_handler(ChatMemberHandler(process_chat_member_transition, ChatMemberHandler.CHAT_MEMBER))

        logger.info("Ultra-Pro-Max Sentinel Core initialized successfully. Polling loop commencing...")
        
        application_builder.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True
        )
    except Exception as boot_exc:
        logger.critical(f"[FATAL SYSTEM CRASH] Application launch aborted: {boot_exc}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
    
