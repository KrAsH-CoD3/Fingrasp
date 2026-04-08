"""Pydantic schemas for request validation on the /save endpoint."""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Any
import re


# ── Security limits ──
MAX_PAYLOAD_BYTES = 512 * 1024  # 512 KB max total payload size
MAX_FINGERPRINT_KEYS = 200  # max top-level keys in fingerprint dict
MAX_NESTING_DEPTH = 12  # max recursion depth for nested objects
MAX_STRING_LENGTH = 100_000  # max length of any single string value
MAX_HASH_LENGTH = 128  # max length of the hash field

# Regex for illegal MongoDB keys: starts with '$' or contains '.'
_ILLEGAL_KEY_PATTERN = re.compile(r"^[$.]")


def _sanitize_data(obj: Any) -> Any:
    """
    Recursively sanitize data to prevent NoSQL injection.
    Removes keys that match _ILLEGAL_KEY_PATTERN.
    """
    if isinstance(obj, dict):
        sanitized = {}
        for key, value in obj.items():
            # Skip MongoDB operator keys ($) and dot notation keys
            if isinstance(key, str):
                if _ILLEGAL_KEY_PATTERN.search(key):
                    continue
                sanitized[key] = _sanitize_data(value)
            else:
                sanitized[key] = _sanitize_data(value)
        return sanitized
    elif isinstance(obj, list):
        return [_sanitize_data(item) for item in obj]
    else:
        return obj


def _check_depth(obj: Any, current: int = 0) -> int:
    """Return the maximum nesting depth of a JSON-like object."""
    if current > MAX_NESTING_DEPTH:
        raise ValueError(
            f"Payload nesting exceeds maximum depth of {MAX_NESTING_DEPTH}"
        )
    if isinstance(obj, dict):
        if not obj:
            return current
        return max(_check_depth(v, current + 1) for v in obj.values())
    if isinstance(obj, list):
        if not obj:
            return current
        return max(_check_depth(v, current + 1) for v in obj)
    return current


def _check_strings(obj: Any) -> None:
    """Reject any string value or key that exceeds MAX_STRING_LENGTH."""
    if isinstance(obj, str):
        if len(obj) > MAX_STRING_LENGTH:
            raise ValueError(
                f"String value exceeds maximum length of {MAX_STRING_LENGTH}"
            )
    elif isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(k, str) and len(k) > MAX_STRING_LENGTH:
                raise ValueError(
                    f"Dictionary key exceeds maximum length of {MAX_STRING_LENGTH}"
                )
            _check_strings(v)
    elif isinstance(obj, list):
        for v in obj:
            _check_strings(v)


class FingerprintPayload(BaseModel):
    """Schema for the fingerprint data submitted by the frontend."""

    hash: str = Field(
        ...,
        min_length=1,
        max_length=MAX_HASH_LENGTH,
        description="Composite fingerprint hash from MixVisit",
    )
    loadTime: int = Field(
        ...,
        ge=0,
        le=60_000,
        description="Collection time in milliseconds (max 1 minute)",
    )
    fingerprint: dict[str, Any] = Field(
        ...,
        description="Signal dictionary produced by MixVisit",
    )

    @field_validator("hash")
    @classmethod
    def hash_must_be_hex_like(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Hash must not be empty or whitespace")

        # Basic length validation to prevent DoS with extremely large strings
        # and ensure it resembles a valid fingerpirnt hash (e.g. 32-128 hex chars)
        if len(stripped) < 32 or len(stripped) > 128:
            raise ValueError("Hash length is outside acceptable range")

        # Validate hex format
        if not all(c in "0123456789abcdefABCDEF" for c in stripped):
            raise ValueError("Hash must be hexadecimal")
        return stripped

    @field_validator("fingerprint")
    @classmethod
    def fingerprint_key_limit(cls, v: dict) -> dict:
        if len(v) > MAX_FINGERPRINT_KEYS:
            raise ValueError(
                f"Fingerprint contains {len(v)} top-level keys, "
                f"maximum allowed is {MAX_FINGERPRINT_KEYS}"
            )
        return v

    @model_validator(mode="after")
    def enforce_depth_and_size(self) -> FingerprintPayload:
        # Sanitize fingerprint data to prevent NoSQL injection
        original_key_count = (
            len(self.fingerprint) if isinstance(self.fingerprint, dict) else 0
        )
        self.fingerprint = _sanitize_data(self.fingerprint)
        sanitized_key_count = (
            len(self.fingerprint) if isinstance(self.fingerprint, dict) else 0
        )

        if sanitized_key_count < original_key_count:
            import logging

            logger = logging.getLogger(__name__)
            logger.warning(
                f"NoSQL sanitization removed {original_key_count - sanitized_key_count} keys from fingerprint"
            )

        # Check nesting depth
        _check_depth(self.fingerprint)

        # Check for oversized strings (e.g. someone injecting huge blobs)
        _check_strings(self.fingerprint)

        return self


class TurnstileValidationRequest(BaseModel):
    """Schema for public self-service flow using Turnstile and honeypot."""

    cf_turnstile_response: str = Field(
        ...,
        min_length=1,
        description="Turnstile challenge token",
    )
    honeypot_email: str | None = Field(
        default=None,
        max_length=100,
        description="Honeypot field that must be empty",
    )
    honeypot_user_id: str | None = Field(
        default=None,
        max_length=100,
        description="Honeypot field that must be empty",
    )
    honeypot_website: str | None = Field(
        default=None,
        max_length=100,
        description="Honeypot field that must be empty",
    )
    time_to_solve: int | None = Field(
        default=None,
        description="Time taken between page load and submission in milliseconds",
    )
    interaction_score: int | None = Field(
        default=0,
        description="Behavioral interaction score based on mouse/keyboard events",
    )


class MixVisitPayload(FingerprintPayload):
    """Schema for fingerprint submission with session token."""

    session_token: str = Field(
        ...,
        min_length=36,
        max_length=36,
        description="Session token from successful validation",
    )
    device_model: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
        description="User-provided device model",
    )


# --- Response Schemas ---


class SuccessResponse(BaseModel):
    """Standard success response."""

    message: str


class ErrorResponse(SuccessResponse):
    """Standard error response."""

    error_code: str


class SessionResponse(SuccessResponse):
    """Response containing the short-lived session token."""

    session_token: str
