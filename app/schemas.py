"""Pydantic schemas for request validation on the /save endpoint."""

from __future__ import annotations
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Any
import sys


# ── Security limits ──
MAX_PAYLOAD_BYTES = 512 * 1024       # 512 KB max total payload size
MAX_FINGERPRINT_KEYS = 200           # max top-level keys in fingerprint dict
MAX_NESTING_DEPTH = 12               # max recursion depth for nested objects
MAX_STRING_LENGTH = 100_000          # max length of any single string value
MAX_HASH_LENGTH = 128                # max length of the hash field


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
    """Reject any string value that exceeds MAX_STRING_LENGTH."""
    if isinstance(obj, str):
        if len(obj) > MAX_STRING_LENGTH:
            raise ValueError(
                f"String value exceeds maximum length of {MAX_STRING_LENGTH}"
            )
    elif isinstance(obj, dict):
        for v in obj.values():
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
        le=300_000,
        description="Collection time in milliseconds (max 5 min)",
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
        # Check nesting depth
        _check_depth(self.fingerprint)

        # Check for oversized strings (e.g. someone injecting huge blobs)
        _check_strings(self.fingerprint)

        # Rough byte-size check via sys.getsizeof on the dict repr
        payload_estimate = sys.getsizeof(str(self.fingerprint))
        if payload_estimate > MAX_PAYLOAD_BYTES:
            raise ValueError(
                f"Estimated payload size ({payload_estimate} bytes) "
                f"exceeds maximum of {MAX_PAYLOAD_BYTES} bytes"
            )

        return self
