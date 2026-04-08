"""FastAPI API endpoints for fingerprint collection."""

from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse
import uuid
import logging
import httpx

from app.device_detection import validate_device_model
from app.security import anonymize_ip, get_real_ip
from app.config import settings
from app.limiter import limiter
from app.schemas import (
    TurnstileValidationRequest,
    ErrorResponse,
    MixVisitPayload,
    SuccessResponse,
    SessionResponse,
)

logger = logging.getLogger(__name__)

# Shared httpx client with connection pooling for Turnstile verification
_turnstile_client = httpx.AsyncClient(
    base_url="https://challenges.cloudflare.com",
    timeout=10.0,
)


router = APIRouter(prefix="/api", tags=["api"])


@limiter.limit(settings.RATE_LIMIT_API)
@router.post("/validate-turnstile")
async def validate_turnstile(
    request: Request,
    body: TurnstileValidationRequest,
) -> JSONResponse:
    """
    Validate Turnstile challenge and behavioral metrics, then generate a session token.
    """
    # Check Honeypots (Multi-layered bait)
    if body.honeypot_email or body.honeypot_user_id or body.honeypot_website:
        # Silently fail for bots
        logger.warning(
            f"Submission rejected: Layered honeypot triggered by {get_real_ip(request)}"
        )
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content=ErrorResponse(
                error_code="FP_ERR_BOT_DETECTED",
                message="Security verification failed.",
            ).model_dump(),
        )

    # Check Timing & Interaction Verification
    # bots often have perfect timing or zero interaction
    if body.time_to_solve is not None:
        # Too fast is always suspicious
        if body.time_to_solve < 2500:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content=ErrorResponse(
                    error_code="FP_ERR_BOT_DETECTED",
                    message="Submission too fast.",
                ).model_dump(),
            )

        # Zero interaction after significant time is highly suspicious of headless automation
        # We check if score is < 5 (e.g. they solved turnstile but never moved mouse/typed)
        if body.interaction_score is not None and body.interaction_score < 5:
            logger.warning(
                f"Bot suspected for {get_real_ip(request)}: Low interaction score ({body.interaction_score})"
            )
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content=ErrorResponse(
                    error_code="FP_ERR_BOT_DETECTED",
                    message="Unusual behavior detected.",
                ).model_dump(),
            )

    # Verify Turnstile token with Cloudflare
    if not settings.TURNSTILE_SECRET_KEY:
        logger.error("Turnstile secret key not configured - rejecting request")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=ErrorResponse(
                error_code="FP_ERR_CONFIG_ERROR",
                message="Security verification service not configured.",
            ).model_dump(),
        )
    else:
        try:
            response = await _turnstile_client.post(
                "/turnstile/v0/siteverify",
                data={
                    "secret": settings.TURNSTILE_SECRET_KEY,
                    "response": body.cf_turnstile_response,
                    "remoteip": get_real_ip(request),
                },
                timeout=settings.API_TIMEOUT,
            )
            response.raise_for_status()
            data = response.json()

            if not data.get("success"):
                logger.warning(
                    f"Turnstile failed for {get_real_ip(request)}: {data.get('error-codes')}"
                )
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content=ErrorResponse(
                        error_code="FP_ERR_CAPTCHA_FAILED",
                        message="Security check failed. Please refresh.",
                    ).model_dump(),
                )
        except httpx.HTTPError as exc:
            logger.error(f"Cloudflare Turnstile API error: {exc}")
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content=ErrorResponse(
                    error_code="FP_ERR_EXTERNAL_SERVICE",
                    message="Verification service temporarily unavailable.",
                ).model_dump(),
            )

    # Generate Session Token
    db = request.app.state.db
    session_token = str(uuid.uuid4())
    await db[settings.TEMP_SESSION_COLLECTION_NAME].insert_one(
        {
            "session_token": session_token,
            "expires_at": datetime.now(timezone.utc)
            + timedelta(minutes=settings.TEMP_SESSION_EXPIRY_MINUTES),
        }
    )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=SessionResponse(
            session_token=session_token,
            message="Verification successful. Session initiated.",
        ).model_dump(),
    )


@limiter.limit(settings.RATE_LIMIT_SAVE)
@router.post("/save")
async def save(
    request: Request,
    payload: MixVisitPayload,
) -> JSONResponse:
    """
    Save fingerprint payload.

    Validation order:
    a. Validate session token exists and is valid
    b. Delete session token immediately (prevent race conditions)
    c. Validate payload fields
    d. Check for duplicates using SHA-256 hash
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

    client_ip = get_real_ip(request)
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

    # ── Persistent Atomic Counter Increment ──
    try:
        await db[settings.COUNTERS_COLLECTION_NAME].update_one(
            {"_id": "total_fingerprints"}, {"$inc": {"count": 1}}, upsert=True
        )
        # Immediate update for this worker's memory cache
        if hasattr(request.app.state, "total_collected"):
            request.app.state.total_collected += 1
    except Exception as e:
        logger.error(f"Failed to increment persistent counter: {e}")

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=SuccessResponse(
            message="Thank you for contributing to this research.",
        ).model_dump(),
    )
