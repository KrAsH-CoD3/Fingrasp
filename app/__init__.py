from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI

from app.routes.fingerprint import router as fingerprint_router
from app.security import SecurityHeadersMiddleware
from app.config import settings
from app.limiter import limiter


def create_app() -> FastAPI:
    application = FastAPI(title=settings.APP_NAME)

    # ── Rate Limiting ──
    application.state.limiter = limiter
    application.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # ── CORS ──
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )

    # ── Secure HTTP Headers ──
    application.add_middleware(SecurityHeadersMiddleware)

    # ── Static Files ──
    application.mount("/static", StaticFiles(directory="static"), name="static")

    # ── Routes ──
    application.include_router(fingerprint_router)

    return application
