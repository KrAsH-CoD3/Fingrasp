from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import logging

from app.limiter import limiter
from app.device_detection.databases import (
    INDIVIDUAL_IPHONE_MODELS,
    INDIVIDUAL_IPAD_MODELS,
    INDIVIDUAL_MAC_MODELS,
    IPHONE_SCREEN_MODELS,
    IPAD_SCREEN_MODELS,
)


router = APIRouter()
templates = Jinja2Templates(directory="templates")
logger = logging.getLogger(__name__)


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
@limiter.limit("20/minute")
async def index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "nonce": request.state.csp_nonce,
            "iphone_models": INDIVIDUAL_IPHONE_MODELS,
            "ipad_models": INDIVIDUAL_IPAD_MODELS,
            "mac_models": INDIVIDUAL_MAC_MODELS,
            "iphone_screen_models": IPHONE_SCREEN_MODELS,
            "ipad_screen_models": IPAD_SCREEN_MODELS,
        },
    )


@router.get("/privacy", response_class=HTMLResponse, include_in_schema=False)
@limiter.limit("20/minute")
async def privacy(request: Request):
    return templates.TemplateResponse(
        "privacy.html", {"request": request, "nonce": request.state.csp_nonce}
    )


@router.get("/how-it-works", response_class=HTMLResponse, include_in_schema=False)
@limiter.limit("20/minute")
async def how_it_works(request: Request):
    return templates.TemplateResponse(
        "how-it-works.html", {"request": request, "nonce": request.state.csp_nonce}
    )
