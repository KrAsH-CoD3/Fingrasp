from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from datetime import datetime, timezone
import os

load_dotenv()

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

client = AsyncIOMotorClient(os.getenv("MONGODB_URI"))
collection = client[os.getenv("DB_NAME", "fingrasp")]["fingerprints"]


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/save")
async def save(request: Request):
    data = await request.json()
    data["ip"]       = request.client.host
    data["saved_at"] = datetime.now(timezone.utc).isoformat()
    result = await collection.insert_one(data)
    return {"id": str(result.inserted_id)}
