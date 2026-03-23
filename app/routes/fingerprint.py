from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import logging

from app.limiter import limiter


router = APIRouter()
templates = Jinja2Templates(directory="templates")
logger = logging.getLogger(__name__)


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
@limiter.limit("20/minute")
async def index(request: Request):
    return templates.TemplateResponse(
        "index.html", {"request": request, "nonce": request.state.csp_nonce}
    )


@router.get("/privacy", response_class=HTMLResponse, include_in_schema=False)
@limiter.limit("20/minute")
async def privacy(request: Request):
    return templates.TemplateResponse(
        "privacy.html", {"request": request, "nonce": request.state.csp_nonce}
    )
