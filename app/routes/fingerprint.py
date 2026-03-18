from fastapi import APIRouter, Request, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime, timezone
from pydantic import ValidationError
import logging

from app.security import anonymize_ip, is_trusted_origin
from app.schemas import FingerprintPayload
from app.config import settings
from app.database import db
from app.limiter import limiter


router = APIRouter()
templates = Jinja2Templates(directory="templates")
logger = logging.getLogger(__name__)


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "nonce": request.state.csp_nonce}
    )


@router.get("/privacy", response_class=HTMLResponse)
async def privacy(request: Request):
    return templates.TemplateResponse(
        "privacy.html",
        {"request": request, "nonce": request.state.csp_nonce}
    )


@router.post("/save", status_code=status.HTTP_201_CREATED)
@limiter.limit(settings.RATE_LIMIT_SAVE)
async def save(request: Request):
    # ── Trusted Origin Check ──
    if not is_trusted_origin(request):
        logger.warning(
            f"Blocked untrusted origin: "
            f"Origin={request.headers.get('origin')!r}  "
            f"Referer={request.headers.get('referer')!r}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Request origin not allowed",
        )

    # ── Parse raw JSON ──
    try:
        raw = await request.json()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Request body is not valid JSON",
        )

    # ── Validate against schema ──
    try:
        payload = FingerprintPayload(**raw)
    except ValidationError as e:
        logger.warning(f"Validation failed: {e.error_count()} error(s)\n{e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.errors(),
        )

    # ── Build document from validated data only ──
    validated_data = payload.model_dump()

    # IP Anonymization — mask last octet before persisting
    raw_ip = request.client.host if request.client else "0.0.0.0"
    validated_data["ip"] = anonymize_ip(raw_ip) if settings.ANONYMIZE_IP else raw_ip

    validated_data["saved_at"] = datetime.now(timezone.utc).isoformat()

    try:
        result = await db["fingerprints"].insert_one(validated_data)
        logger.info(f"Saved fingerprint. ID: {result.inserted_id}")
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"status": "ok"},
        )
    except Exception as e:
        logger.error(f"Failed to save fingerprint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )
