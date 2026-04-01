from telegram.error import TimedOut, NetworkError, TelegramError
from datetime import datetime, timedelta, timezone
from telegram import Update
from functools import wraps
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
import secrets
import logging
import re
import asyncio

from app.config import settings


ALLOWED_USER_ID = settings.TELEGRAM_ALLOWED_USER_ID
BOT_TOKEN = settings.TELEGRAM_BOT_TOKEN
BASE_URL = settings.BASE_URL
CODE_EXPIRY_HOURS = settings.CODE_EXPIRY_HOURS
COLLECTION_NAME = settings.COLLECTION_NAME


logger = logging.getLogger(__name__)


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
    await safe_reply(
        update,
        "Welcome to Fingrasp Bot!\n\n"
        "Available commands:\n"
        "/generate - Generate a new access code\n"
        "/codes - List all access codes\n"
        "/revoke {code} - Revoke an access code\n"
        "/help - Show help menu",
    )


@authorized
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command - list all available commands."""
    await safe_reply(
        update,
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

    await safe_reply(
        update,
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
        await safe_reply(update, "No access codes found.")
        return

    lines = ["📋 Access Codes:\n"]
    for code_doc in codes:
        code = code_doc["code"]
        expires_at = code_doc["expires_at"]
        link = f"{BASE_URL}/?code={code}"
        expiry_str = expires_at.strftime("%Y-%m-%d %H:%M UTC")

        lines.append(f"• <code>{code}</code>\n Link: {link}\n Expires: {expiry_str}\n")

    await safe_reply(
        update,
        "\n".join(lines),
        parse_mode="HTML",
        disable_web_page_preview=True,
    )


@authorized
async def revoke_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /revoke command - delete a specific access code."""
    args = context.args
    if not args:
        await safe_reply(update, "Usage: /revoke {code}")
        return

    code = args[0]

    if not validate_code_format(code):
        logger.warning(
            "Invalid code format in revoke attempt: user_id=%s",
            update.effective_user.id,
        )
        await safe_reply(
            update, "❌ Invalid code format. Code must be exactly 6 digits."
        )
        return

    db = context.bot_data["db"]

    existing = await db[COLLECTION_NAME].find_one({"code": code})
    if not existing:
        await safe_reply(
            update, f"❌ Code <code>{code}</code> not found.", parse_mode="HTML"
        )
        return

    await db[COLLECTION_NAME].delete_one({"code": code})

    logger.info(
        "Access code revoked: user_id=%s",
        update.effective_user.id,
    )

    await safe_reply(
        update,
        f"✅ Code <code>{code}</code> has been revoked.",
        parse_mode="HTML",
    )


@authorized
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle non-command messages from authorized users."""
    await safe_reply(
        update, "I only understand commands! Type /help to see what I can do. 🤖"
    )


async def setup_bot_database(
    telegram_app: Application | None, client=None, db=None
) -> None:
    """Initialize bot data using an existing database connection."""
    if telegram_app is None:
        return

    # Must setup db before initializing, so db is avilable when initializing
    telegram_app.bot_data["db"] = db
    telegram_app.bot_data["db_client"] = client

    # Now db is available, we can initialize and start the bot
    await telegram_app.initialize()
    await telegram_app.start()

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors in the telegram bot."""
    logger.error(f"Exception while handling an update: {context.error}")
    if isinstance(context.error, TimedOut):
        logger.warning("Telegram API timed out - network issue or slow connection")
    elif isinstance(context.error, NetworkError):
        logger.warning(f"Network error: {context.error}")
    else:
        logger.exception("Unexpected error in telegram bot")


async def safe_reply(update: Update, text: str, max_retries: int = 3, **kwargs) -> bool:
    """
    Send reply with retry logic for network errors.

    Args:
        update: Telegram update object
        text: Message text to send
        max_retries: Maximum number of retry attempts
        **kwargs: Additional arguments for reply_text

    Returns:
        True if message was sent successfully, False otherwise
    """
    for attempt in range(max_retries):
        try:
            await update.message.reply_text(text, **kwargs)
            return True
        except TimedOut as e:
            if attempt < max_retries - 1:
                wait_time = 2**attempt  # Exponential backoff: 1s, 2s, 4s
                logger.warning(
                    f"Timeout sending message (attempt {attempt + 1}/{max_retries}), "
                    f"retrying in {wait_time}s: {e}"
                )
                await asyncio.sleep(wait_time)
            else:
                logger.error(
                    f"Failed to send message after {max_retries} attempts: {e}"
                )
                return False
        except NetworkError as e:
            if attempt < max_retries - 1:
                wait_time = 2**attempt
                logger.warning(
                    f"Network error (attempt {attempt + 1}/{max_retries}), "
                    f"retrying in {wait_time}s: {e}"
                )
                await asyncio.sleep(wait_time)
            else:
                logger.error(
                    f"Failed to send message after {max_retries} attempts: {e}"
                )
                return False
        except TelegramError as e:
            # Don't retry on other Telegram errors (e.g., blocked user, invalid chat)
            logger.error(f"Telegram error sending message: {e}")
            return False
    return False




def get_telegram_app() -> Application:
    """Get a configured Application instance for webhook integration."""
    if not BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN not set")

    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .connect_timeout(30)
        .read_timeout(30)
        .write_timeout(30)
        .build()
    )

    application.add_error_handler(error_handler)
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("generate", generate_command))
    application.add_handler(CommandHandler("codes", codes_command))
    application.add_handler(CommandHandler("revoke", revoke_command))

    # Fallback handler for non-command text messages
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )
    return application

