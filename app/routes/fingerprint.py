from fastapi import APIRouter, Request, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime, timezone
import logging

from app.database import db

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
    try:
        data = await request.json()
        data["ip"] = request.client.host
        data["saved_at"] = datetime.now(timezone.utc).isoformat()
        
        result = await db["fingerprints"].insert_one(data)
        
        logger.info(f"Successfully saved fingerprint. ID: {result.inserted_id}")
        response = {"status": "ok"}

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=response,
            # headers={"Location": f"/data/{result.inserted_id}"} # Not needed at the moment
        )
    except Exception as e:
        logger.error(f"Failed to save fingerprint: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
