from fastapi import APIRouter, Request, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError
from datetime import datetime, timezone
import logging

from app.database import db
from app.schemas import FingerprintPayload

router = APIRouter()
templates = Jinja2Templates(directory="templates")
logger = logging.getLogger(__name__)


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/privacy", response_class=HTMLResponse)
async def privacy(request: Request):
    return templates.TemplateResponse("privacy.html", {"request": request})


@router.post("/save", status_code=status.HTTP_201_CREATED)
async def save(request: Request):
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
    validated_data["ip"] = request.client.host
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
