from dataclasses import dataclass, field
from dotenv import load_dotenv
import os

load_dotenv()


@dataclass
class Settings:
    APP_NAME: str = "Fingrasp"
    MONGODB_URI: str = os.getenv("MONGODB_URI", "")
    DB_NAME: str = os.getenv("DB_NAME", "fingrasp")

    TRUE_VALUES = {"true", "1", "yes"}
    
    # ── Environment ──
    DEBUG: bool = os.getenv("DEBUG", "true").lower() in TRUE_VALUES
    
    # Only enable HSTS and HTTPS-only rules in production
    STRICT_SECURITY: bool = os.getenv("STRICT_SECURITY", "false").lower() in TRUE_VALUES

    # ── CORS ──
    # Domains allowed to make requests to the API.
    # In production, set ALLOWED_ORIGINS in .env as comma-separated values.
    ALLOWED_ORIGINS: list[str] = field(default_factory=lambda: [
        allowed_origin.strip()
        for allowed_origin in os.getenv(
            "ALLOWED_ORIGINS",
            "http://localhost:8000,http://127.0.0.1:8000"
        ).split(",")
        if allowed_origin.strip()
    ])

    # ── Rate Limiting ──
    RATE_LIMIT_SAVE: str = os.getenv("RATE_LIMIT_SAVE", "5/minute")

    # ── IP Anonymization ──
    # When True, the last octet of IPv4 (or last 80 bits of IPv6) is zeroed
    # before saving to the database.
    ANONYMIZE_IP: bool = os.getenv("ANONYMIZE_IP", "true").lower() in TRUE_VALUES


settings = Settings()
