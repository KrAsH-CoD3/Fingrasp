from dataclasses import dataclass, field
from dotenv import load_dotenv
import os

load_dotenv()


TRUE_VALUES = {"true", "1", "yes"}

# ── Security Configuration ──
MAX_REQUEST_BODY_SIZE = 512 * 1024  # 512 KB max request body


def _validate_mongodb_uri() -> str:
    """Validate that MONGODB_URI is configured."""
    uri = os.getenv("MONGODB_URI", "").strip()
    if not uri:
        # In production, raise an error.
        if os.getenv("STRICT_SECURITY", "false").lower() in TRUE_VALUES:
            raise ValueError(
                "MONGODB_URI environment variable is required in production"
            )
        # For dev, we'll still return empty and let the app fail gracefully
        # Should provide a helpful message.
        return ""
    return uri


@dataclass
class Settings:
    APP_NAME: str = "Fingrasp"
    MONGODB_URI: str = field(default_factory=lambda: _validate_mongodb_uri())
    DB_NAME: str = os.getenv("DB_NAME", "fingrasp")

    # ── Environment ──
    DEBUG: bool = os.getenv("DEBUG", "true").lower() in TRUE_VALUES

    # Only enable HSTS and HTTPS-only rules in production
    STRICT_SECURITY: bool = os.getenv("STRICT_SECURITY", "false").lower() in TRUE_VALUES

    # ── CORS ──
    # Domains allowed to make requests to the API.
    # In production, set ALLOWED_ORIGINS in .env as comma-separated values.
    ALLOWED_ORIGINS: list[str] = field(
        default_factory=lambda: [
            allowed_origin.strip()
            for allowed_origin in os.getenv(
                "ALLOWED_ORIGINS", "http://localhost:8000,http://127.0.0.1:8000"
            ).split(",")
            if allowed_origin.strip()
        ]
    )

    # ── Rate Limiting ──
    RATE_LIMIT_SAVE: str = os.getenv("RATE_LIMIT_SAVE", "5/minute")

    # ── IP Anonymization ──
    # When True, the last octet of IPv4 (or last 80 bits of IPv6) is zeroed
    # before saving to the database.
    ANONYMIZE_IP: bool = os.getenv("ANONYMIZE_IP", "true").lower() in TRUE_VALUES

    # ── Cloudflare Turnstile ──
    TURNSTILE_SITE_KEY: str = os.getenv("TURNSTILE_SITE_KEY", "").strip()
    TURNSTILE_SECRET_KEY: str = os.getenv("TURNSTILE_SECRET_KEY", "").strip()

    # ── Telegram Bot ──
    BASE_URL: str = os.getenv("BASE_URL", "http://localhost:8000")
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_ALLOWED_USER_ID: int = int(os.getenv("TELEGRAM_ALLOWED_USER_ID", "0"))
    TELEGRAM_WEBHOOK_URL: str = BASE_URL + "/webhook"
    TELEGRAM_WEBHOOK_SECRET: str = os.getenv("TELEGRAM_WEBHOOK_SECRET", "")
    CODE_EXPIRY_HOURS: int = int(os.getenv("CODE_EXPIRY_HOURS", "48"))

    # ── MongoDB Collections ──
    ACCESS_CODE_COLLECTION_NAME: str = os.getenv("ACCESS_CODE_COLLECTION_NAME", "access_codes")
    FINGERPRINT_COLLECTION_NAME: str = os.getenv("FINGERPRINT_COLLECTION_NAME", "fingers")
    TEMP_SESSION_COLLECTION_NAME: str = os.getenv("TEMP_SESSION_COLLECTION_NAME", "temp_sessions")
    TEMP_SESSION_EXPIRY_MINUTES: int = int(os.getenv("TEMP_SESSION_EXPIRY_MINUTES", "5"))

    # ── External APIs ──
    # Timeout for external requests like Turnstile siteverify
    API_TIMEOUT: float = float(os.getenv("API_TIMEOUT", "15.0"))


settings = Settings()
