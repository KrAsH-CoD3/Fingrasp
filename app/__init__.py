from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import settings
from app.database import connect_db
from app.routes.fingerprint import router as fingerprint_router


def create_app() -> FastAPI:
    application = FastAPI(title=settings.APP_NAME)
    application.mount("/static", StaticFiles(directory="static"), name="static")
    application.include_router(fingerprint_router)
    return application
