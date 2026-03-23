import re
import secrets
import logging
from datetime import datetime, timedelta, timezone

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from app.config import settings
from app.database import setup_db

logger = logging.getLogger(__name__)

ALLOWED_USER_ID = settings.TELEGRAM_ALLOWED_USER_ID
BOT_TOKEN = settings.TELEGRAM_BOT_TOKEN
BASE_URL = settings.BASE_URL
CODE_EXPIRY_HOURS = settings.CODE_EXPIRY_HOURS
COLLECTION_NAME = settings.COLLECTION_NAME


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


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command - only shows help for authorized users."""
    if not await is_authorized(update):
        logger.warning(
            "Unauthorized start attempt from user_id=%s",
            update.effective_user.id if update.effective_user else "unknown",
        )
        return

    await update.message.reply_text(
        "Welcome to Fingrasp Bot!\n\n"
        "Available commands:\n"
        "/generate - Generate a new access code\n"
        "/codes - List all access codes\n"
        "/revoke <code> - Revoke an access code"
    )


async def generate_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /generate command - generate a new access code."""
    if not await is_authorized(update):
        logger.warning(
            "Unauthorized generate attempt from user_id=%s",
            update.effective_user.id if update.effective_user else "unknown",
        )
        return

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


async def codes_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /codes command - list all access codes."""
    if not await is_authorized(update):
        logger.warning(
            "Unauthorized codes list attempt from user_id=%s",
            update.effective_user.id if update.effective_user else "unknown",
        )
        return

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


async def revoke_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /revoke command - delete a specific access code."""
    if not await is_authorized(update):
        logger.warning(
            "Unauthorized revoke attempt from user_id=%s",
            update.effective_user.id if update.effective_user else "unknown",
        )
        return

    args = context.args
    if not args:
        await update.message.reply_text("Usage: /revoke <code>")
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


async def post_init(application: Application) -> None:
    """Initialize bot data after application starts."""
    client, db = setup_db()
    application.bot_data["db"] = db
    application.bot_data["db_client"] = client
    logger.info("Database connected for Telegram bot")


async def post_shutdown(application: Application) -> None:
    """Cleanup after application stops."""
    client = application.bot_data.get("db_client")
    if client:
        client.close()
        logger.info("Database connection closed")


def main() -> None:
    """Run the Telegram bot."""
    if not BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not set")
        return

    if not ALLOWED_USER_ID:
        logger.error("TELEGRAM_ALLOWED_USER_ID not set")
        return

    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("generate", generate_command))
    application.add_handler(CommandHandler("codes", codes_command))
    application.add_handler(CommandHandler("revoke", revoke_command))

    application.post_init = post_init
    application.post_shutdown = post_shutdown

    logger.info("Starting Telegram bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    main()
