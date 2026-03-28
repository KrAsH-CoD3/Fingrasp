from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from datetime import datetime, timedelta, timezone
from telegram import Update
from typing import Optional
from functools import wraps
import secrets
import logging
import re

from app.config import settings
from app.database import setup_db


logger = logging.getLogger(__name__)

ALLOWED_USER_ID = settings.TELEGRAM_ALLOWED_USER_ID
BOT_TOKEN = settings.TELEGRAM_BOT_TOKEN
BASE_URL = settings.BASE_URL
CODE_EXPIRY_HOURS = settings.CODE_EXPIRY_HOURS
COLLECTION_NAME = settings.COLLECTION_NAME

# Webhook configuration
TELEGRAM_WEBHOOK_SECRET = settings.TELEGRAM_WEBHOOK_SECRET
TELEGRAM_WEBHOOK_URL = settings.TELEGRAM_WEBHOOK_URL


def generate_code() -> str:
    """Generate 6-digit numeric code."""
    return "".join(secrets.choice("0123456789") for _ in range(6))


def validate_code_format(code: str) -> bool:
    """Validate that code is exactly 6 digits."""
    return bool(re.match(r"^\d{6}$", code))


async def is_authorized(update: Update) -> bool:
    """Check if the user is authorized to use the bot."""
    return (
        update.effective_user is not None
        and update.effective_user.id == ALLOWED_USER_ID
    )


def authorized(func):
    """Decorator to check if user is authorized before executing command."""

    @wraps(func)
    async def wrapper(
        update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs
    ):
        if not await is_authorized(update):
            logger.warning(
                "Unauthorized attempt from user_id=%s",
                update.effective_user.id if update.effective_user else "unknown",
            )
            return
        return await func(update, context, *args, **kwargs)

    return wrapper


@authorized
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command - only shows help for authorized users."""
    await update.message.reply_text(
        "Welcome to Fingrasp Bot!\n\n"
        "Available commands:\n"
        "/generate - Generate a new access code\n"
        "/codes - List all access codes\n"
        "/revoke {code} - Revoke an access code\n"
        "/help - Show help menu"
    )


@authorized
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command - list all available commands."""
    await update.message.reply_text(
        "🆘 <b>Fingrasp Bot Help</b>\n\n"
        "Available commands:\n\n"
        "• /generate - Generate a new 6-digit access code and link.\n"
        "• /codes - List all active access codes.\n"
        "• /revoke {code} - Immediately revoke a specific code.\n"
        "• /help - Show this help message.\n"
        "• /start - Show welcome message.",
        parse_mode="HTML",
    )


@authorized
async def generate_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /generate command - generate a new access code."""
    db = context.bot_data["db"]

    code = generate_code()

    created_at = datetime.now(timezone.utc)
    expires_at = created_at + timedelta(hours=CODE_EXPIRY_HOURS)

    await db[COLLECTION_NAME].insert_one(
        {
            "code": code,
            "created_at": created_at,
            "expires_at": expires_at,
        }
    )

    logger.info("Access code generated: user_id=%s", update.effective_user.id)

    link = f"{BASE_URL}/?code={code}"
    expiry_str = expires_at.strftime("%Y-%m-%d %H:%M UTC")

    await update.message.reply_text(
        f"✅ Access code generated!\n\n"
        f"<b>Code:</b> <code>{code}</code>\n"
        f"<b>Link:</b> {link}\n"
        f"<b>Expires:</b> {expiry_str}",
        parse_mode="HTML",
        disable_web_page_preview=True,
    )


@authorized
async def codes_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /codes command - list all access codes."""
    db = context.bot_data["db"]

    cursor = await db[COLLECTION_NAME].find({})
    cursor = cursor.sort("created_at", 1)
    codes = await cursor.to_list(length=None)

    if not codes:
        await update.message.reply_text("No access codes found.")
        return

    lines = ["📋 Access Codes:\n"]
    for code_doc in codes:
        code = code_doc["code"]
        expires_at = code_doc["expires_at"]
        link = f"{BASE_URL}/?code={code}"
        expiry_str = expires_at.strftime("%Y-%m-%d %H:%M UTC")

        lines.append(f"• <code>{code}</code>\n Link: {link}\n Expires: {expiry_str}\n")

    await update.message.reply_text(
        "\n".join(lines),
        parse_mode="HTML",
        disable_web_page_preview=True,
    )


@authorized
async def revoke_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /revoke command - delete a specific access code."""
    args = context.args
    if not args:
        await update.message.reply_text("Usage: /revoke {code}")
        return

    code = args[0]

    if not validate_code_format(code):
        logger.warning(
            "Invalid code format in revoke attempt: user_id=%s",
            update.effective_user.id,
        )
        await update.message.reply_text(
            "❌ Invalid code format. Code must be exactly 6 digits."
        )
        return

    db = context.bot_data["db"]

    existing = await db[COLLECTION_NAME].find_one({"code": code})
    if not existing:
        await update.message.reply_text(
            f"❌ Code <code>{code}</code> not found.", parse_mode="HTML"
        )
        return

    await db[COLLECTION_NAME].delete_one({"code": code})

    logger.info(
        "Access code revoked: user_id=%s",
        update.effective_user.id,
    )

    await update.message.reply_text(
        f"✅ Code <code>{code}</code> has been revoked.",
        parse_mode="HTML",
    )


@authorized
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle non-command messages from authorized users."""
    await update.message.reply_text(
        "I only understand commands! Type /help to see what I can do. 🤖"
    )


async def setup_bot_database(
    telegram_app: Optional[Application], client=None, db=None
) -> None:
    """Initialize bot data using an existing database connection."""
    if telegram_app is None:
        return

    # Must setup db before initializing, so db is avilable when initializing
    telegram_app.bot_data["db"] = db
    telegram_app.bot_data["db_client"] = client
    await telegram_app.initialize()
    await telegram_app.start()  # Must start to process updates


async def close_bot_database(telegram_app: Application) -> None:
    """Cleanup after application stops."""
    client = telegram_app.bot_data.get("db_client")
    if client:
        client.close()
        logger.info("Database connection closed")


def get_application() -> Application:
    """Get a configured Application instance for webhook integration."""
    if not BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN not set")

    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("generate", generate_command))
    application.add_handler(CommandHandler("codes", codes_command))
    application.add_handler(CommandHandler("revoke", revoke_command))

    # Fallback handler for non-command text messages
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )

    # application.post_init = setup_bot_database
    # application.post_shutdown = close_bot_database

    return application


async def setup_webhook(application: Application) -> None:
    """Set up the webhook with Telegram servers."""
    if not TELEGRAM_WEBHOOK_URL or not TELEGRAM_WEBHOOK_SECRET:
        logger.warning("Webhook URL or secret not configured")
        return

    await application.bot.set_webhook(
        url=TELEGRAM_WEBHOOK_URL,
        secret_token=TELEGRAM_WEBHOOK_SECRET,
        allowed_updates=Update.ALL_TYPES,
    )
    logger.info(f"Webhook set to: {TELEGRAM_WEBHOOK_URL}")


async def remove_webhook(application: Application) -> None:
    """Remove the webhook from Telegram servers."""
    await application.bot.delete_webhook()
    logger.info("Webhook removed")


def main() -> None:
    """Run the Telegram bot."""
    if not BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not set")
        return

    if not ALLOWED_USER_ID:
        logger.error("TELEGRAM_ALLOWED_USER_ID not set")
        return

    application = get_application()

    # Check if webhook mode is configured
    if TELEGRAM_WEBHOOK_URL and TELEGRAM_WEBHOOK_SECRET:
        logger.info("Starting Telegram bot in WEBHOOK mode...")
        # run_webhook is BLOCKING and manages its own loop.
        # We pass webhook_url here so it calls set_webhook for us.
        application.run_webhook(
            listen="0.0.0.0",
            port=8443,
            secret_token=TELEGRAM_WEBHOOK_SECRET,
            url_path="webhook",
            webhook_url=TELEGRAM_WEBHOOK_URL,
            allowed_updates=Update.ALL_TYPES,
        )
    else:
        logger.info("Starting Telegram bot in POLLING mode...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    main()
