"""FastAPI API endpoints for fingerprint collection."""

from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse
import uuid

from app.device_detection import validate_device_model
from app.security import anonymize_ip
from app.config import settings
from app.limiter import limiter
from app.schemas import (
    CodeValidationRequest,
    TurnstileValidationRequest,
    ErrorResponse,
    MixVisitPayload,
    SuccessResponse,
    SessionResponse,
)
import httpx


router = APIRouter(prefix="/api", tags=["api"])


@limiter.limit("10/minute")
@router.post("/validate-code")
async def validate_code(
    request: Request,
    body: CodeValidationRequest,
) -> JSONResponse:
    """
    Validate code and generate a short-lived session token.
    """
    db = request.app.state.db

    # Atomic consumption: burn the code instantly regardless of what happens next
    code_doc = await db[settings.ACCESS_CODE_COLLECTION_NAME].find_one_and_delete(
        {"code": body.code}
    )
    if not code_doc:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content=ErrorResponse(
                error_code="FP_ERR_INVALID",
                message="Access code is not valid.",
            ).model_dump(),
        )

    # Manual check in case the DB TTL cycle hasn't hit yet
    expires_at = code_doc.get("expires_at")
    if expires_at:
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if expires_at < datetime.now(timezone.utc):
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content=ErrorResponse(
                    error_code="FP_ERR_INVALID",
                    message="Access code is expired.",
                ).model_dump(),
            )

    # Generate a short-lived session token
    session_token = str(uuid.uuid4())
    await db[settings.TEMP_SESSION_COLLECTION_NAME].insert_one({
        "session_token": session_token,
        "expires_at": datetime.now(timezone.utc) + timedelta(minutes=settings.TEMP_SESSION_EXPIRY_MINUTES)
    })

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=SessionResponse(
            session_token=session_token,
            message="Code valid. Session initiated.",
        ).model_dump(),
    )


@limiter.limit("5/minute")
@router.post("/validate-turnstile")
async def validate_turnstile(
    request: Request,
    body: TurnstileValidationRequest,
) -> JSONResponse:
    """
    Validate Turnstile challenge and behavioral metrics, then generate a session token.
    """
    # 1. Check Honeypot
    if body.honeypot_email:
        # Silently fail for bots
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content=ErrorResponse(
                error_code="FP_ERR_BOT_DETECTED",
                message="Invalid submission.",
            ).model_dump(),
        )

    # 2. Check Timing Verification (e.g. less than 2.5 seconds is suspicious)
    if body.time_to_solve is not None and body.time_to_solve < 2500:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content=ErrorResponse(
                error_code="FP_ERR_BOT_DETECTED",
                message="Submission too fast.",
            ).model_dump(),
        )

    # 3. Verify Turnstile token with Cloudflare
    if not settings.TURNSTILE_SECRET_KEY:
        # If no key is set, we bypass validation for local dev (warning: only for dev)
        pass
    else:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://challenges.cloudflare.com/turnstile/v0/siteverify",
                data={
                    "secret": settings.TURNSTILE_SECRET_KEY,
                    "response": body.cf_turnstile_response,
                    "remoteip": request.client.host if request.client else None,
                },
                timeout=10.0,
            )
            data = response.json()
            if not data.get("success"):
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content=ErrorResponse(
                        error_code="FP_ERR_CAPTCHA_FAILED",
                        message="CAPTCHA validation failed.",
                    ).model_dump(),
                )

    # 4. Generate Session Token
    db = request.app.state.db
    session_token = str(uuid.uuid4())
    await db[settings.TEMP_SESSION_COLLECTION_NAME].insert_one({
        "session_token": session_token,
        "expires_at": datetime.now(timezone.utc) + timedelta(minutes=settings.TEMP_SESSION_EXPIRY_MINUTES)
    })

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=SessionResponse(
            session_token=session_token,
            message="Verification successful. Session initiated.",
        ).model_dump(),
    )


@limiter.limit("10/minute")
@router.post("/save")
async def save(
    request: Request,
    payload: MixVisitPayload,
) -> JSONResponse:
    """
    Save fingerprint payload.

    Validation order per Section 7:
    a. Validate code exists, not expired (Section 7.1)
    b. Delete code immediately (prevent race conditions)
    c. Validate payload fields (Section 7.2)
    d. Check for duplicates using SHA-256 hash (Section 7.3)
    e. Save fingerprint
    """
    db = request.app.state.db
    # Atomically verify and consume the session token
    session_doc = await db[settings.TEMP_SESSION_COLLECTION_NAME].find_one_and_delete(
        {"session_token": payload.session_token}
    )
    if not session_doc:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content=ErrorResponse(
                error_code="FP_ERR_SESSION_INVALID",
                message="Session invalid or expired.",
            ).model_dump(),
        )

    # Manual check in case the DB TTL cycle hasn't hit yet
    expires_at = session_doc.get("expires_at")
    if expires_at:
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if expires_at < datetime.now(timezone.utc):
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content=ErrorResponse(
                    error_code="FP_ERR_SESSION_INVALID",
                    message="Session has expired.",
                ).model_dump(),
            )

    existing = await db[settings.FINGERPRINT_COLLECTION_NAME].find_one(
        {"hash": payload.hash}
    )
    if existing:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=ErrorResponse(
                error_code="FP_ERR_DUPLICATE",
                message="Duplicate submission.",
            ).model_dump(),
        )

    client_ip = request.client.host if request.client else "0.0.0.0"
    anonymized_ip = anonymize_ip(client_ip)

    device_name = validate_device_model(payload.device_model, payload.fingerprint)

    fingerprint_doc = {
        "hash": payload.hash,
        "loadTime": payload.loadTime,
        "fingerprint": payload.fingerprint,
        "device_name": device_name,
        "ip_address": anonymized_ip,
        "created_at": datetime.now(timezone.utc),
    }

    await db[settings.FINGERPRINT_COLLECTION_NAME].insert_one(fingerprint_doc)

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=SuccessResponse(
            message="Thank you for contributing to this research.",
        ).model_dump(),
    )
