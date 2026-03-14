from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime, timezone

from app.database import db

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.post("/save")
async def save(request: Request):
    data = await request.json()
    data["ip"] = request.client.host
    data["saved_at"] = datetime.now(timezone.utc).isoformat()
    result = await db["fingerprints"].insert_one(data)
    return {"id": str(result.inserted_id)}
