"""FastAPI API endpoints for fingerprint collection."""

from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse
from datetime import datetime, timezone

from app.device_detection import validate_device_model
from app.security import anonymize_ip
from app.config import settings
from app.limiter import limiter
from app.schemas import (
    CodeValidationRequest,
    ErrorResponse,
    MixVisitPayload,
    SuccessResponse,
)


router = APIRouter(prefix="/api", tags=["api"])


@limiter.limit("10/minute")
@router.post("/validate-code")
async def validate_code(
    request: Request,
    body: CodeValidationRequest,
) -> JSONResponse:
    """
    Pre-flight code check for manual flow.
    Validates code exists and is not expired.
    Does NOT delete the code (only validates).
    """
    db = request.app.state.db

    code_doc = await db[settings.COLLECTION_NAME].find_one({"code": body.code})

    if not code_doc:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content=ErrorResponse(
                error_code="FP_ERR_INVALID",
                message="Access code is not valid.",
            ).model_dump(),
        )

    expires_at = code_doc.get("expires_at")
    if expires_at:
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if expires_at < datetime.now(timezone.utc):
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content=ErrorResponse(
                    error_code="FP_ERR_INVALID",
                    message="Access code is not valid.",
                ).model_dump(),
            )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=SuccessResponse(
            message="Code is valid.",
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

    code_doc = await db[settings.COLLECTION_NAME].find_one_and_delete(
        {"code": payload.access_code}
    )

    if not code_doc:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content=ErrorResponse(
                error_code="FP_ERR_INVALID",
                message="Access code is not valid.",
            ).model_dump(),
        )

    expires_at = code_doc.get("expires_at")
    if expires_at:
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if expires_at < datetime.now(timezone.utc):
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content=ErrorResponse(
                    error_code="FP_ERR_INVALID",
                    message="Access code is not valid.",
                ).model_dump(),
            )

    existing = await db["fingerprints"].find_one({"hash": payload.hash})
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

    await db["fingerprints"].insert_one(fingerprint_doc)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=SuccessResponse(
            message="Thank you for contributing to this research.",
        ).model_dump(),
    )
