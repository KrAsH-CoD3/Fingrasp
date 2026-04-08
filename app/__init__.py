from fastapi import FastAPI, Request
from starlette.types import ASGIApp, Receive, Scope, Send
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from starlette.responses import Response
import logging

from app.routes.fingerprint import router as fingerprint_router
from app.config import settings, MAX_REQUEST_BODY_SIZE
from app.routes.api import router as api_router
from app.database import setup_db
from app.limiter import limiter
from app.security import (
    SecurityValidationMiddleware,
    SecurityHeadersMiddleware,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class BodySizeLimitMiddleware:
    """Middleware to limit request body size without pre-consuming the body."""

    def __init__(self, app: ASGIApp, max_size: int):
        self.app = app
        self.max_size = max_size

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        method = scope.get("method", "GET")
        if method in ("GET", "HEAD", "OPTIONS", "DELETE"):
            await self.app(scope, receive, send)
            return

        # Fast path: check Content-Length header
        for name, value in scope.get("headers", []):
            if name.lower() == b"content-length":
                try:
                    if int(value) > self.max_size:
                        response = Response(
                            content='{"detail": "Request body exceeds maximum size"}',
                            status_code=413,
                            headers={"Content-Type": "application/json"},
                        )
                        await response(scope, receive, send)
                        return
                except (ValueError, TypeError):
                    pass

        # Wrap receive to enforce limit on chunked bodies
        body_size = 0
        exceeded = False

        async def wrapped_receive():
            nonlocal body_size, exceeded
            if exceeded:
                return {"type": "http.disconnect"}
            message = await receive()
            if message.get("type") == "http.request":
                body_size += len(message.get("body", b""))
                if body_size > self.max_size:
                    exceeded = True
            return message

        await self.app(scope, wrapped_receive, send)


class RateLimitedStaticFiles(StaticFiles):
    """StaticFiles wrapper with rate limiting support."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._rate_limits = {}
        self._cleanup_counter = 0

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request = Request(scope)
            from app.security import get_real_ip
            import time

            key = f"static:{get_real_ip(request)}"

            now = time.time()
            window_start = now - 60  # 60 second window

            # Cleanup old entries every 10 requests to prevent memory growth
            self._cleanup_counter += 1
            if self._cleanup_counter >= 10:
                self._cleanup_counter = 0
                self._cleanup_old_entries(now, window_start)

            # Get or create rate limit entry atomically
            if key not in self._rate_limits:
                self._rate_limits[key] = []

            # Filter to only keep timestamps within the window
            self._rate_limits[key] = [
                ts for ts in self._rate_limits[key] if ts > window_start
            ]

            # Check if over limit (20 requests per minute)
            if len(self._rate_limits[key]) >= 20:
                response = Response(
                    content='{"error_code": "FP_ERR_RATE_LIMITED", "message": "Rate limit exceeded"}',
                    status_code=429,
                    headers={
                        "Retry-After": "60",
                        "Content-Type": "application/json",
                    },
                )
                await response(scope, receive, send)
                return

            self._rate_limits[key].append(now)

        await super().__call__(scope, receive, send)

    def _cleanup_old_entries(self, now: float, window_start: float):
        """Remove rate limit entries for IPs with no recent activity to prevent memory leak."""
        keys_to_remove = [
            k
            for k, timestamps in self._rate_limits.items()
            if not timestamps or all(ts <= window_start for ts in timestamps)
        ]
        for k in keys_to_remove:
            del self._rate_limits[k]


@asynccontextmanager
async def lifespan(application: FastAPI):
    # ── Database Setup ──
    client, db = setup_db()
    application.state.db = db

    # ── Persistent Global Counter Setup ──
    # Load once on startup for high-speed page loads
    try:
        counter_doc = await db[settings.COUNTERS_COLLECTION_NAME].find_one(
            {"_id": "total_fingerprints"}
        )
        if not counter_doc:
            initial_count = await db[
                settings.FINGERPRINT_COLLECTION_NAME
            ].count_documents({})
            await db[settings.COUNTERS_COLLECTION_NAME].insert_one(
                {"_id": "total_fingerprints", "count": initial_count}
            )
        else:
            initial_count = counter_doc.get("count", 0)

        application.state.total_collected = initial_count
        logger.info(f"Persistent counter initialized at {initial_count}")
    except Exception as e:
        logger.error(f"Failed to initialize persistent counter: {e}")
        application.state.total_collected = 0

    # ── Database Index Verification (TTL) ──
    from pymongo import ASCENDING

    for collection in [
        settings.TEMP_SESSION_COLLECTION_NAME,
    ]:
        try:
            await db._db[collection].create_index(
                [("expires_at", ASCENDING)], expireAfterSeconds=0
            )
            logger.info(f"Verified TTL index on {collection}")
        except Exception as e:
            logger.error(f"TTL index sync error: {e}")

    yield

    # ── Shutdown ──
    if client:
        client.close()
        logger.info("Database connection closed")


def create_app() -> FastAPI:
    application = FastAPI(title=settings.APP_NAME, lifespan=lifespan)

    # ── Static Files ──
    # Rate-limited static files: 20 requests/minute per IP
    application.mount(
        "/static", RateLimitedStaticFiles(directory="static", html=True), name="static"
    )

    # ── Rate Limiting ──
    application.state.limiter = limiter
    application.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # ── Routes ──
    application.include_router(fingerprint_router)
    application.include_router(api_router)

    # ── Request Body Size Limit ──
    application.add_middleware(BodySizeLimitMiddleware, max_size=MAX_REQUEST_BODY_SIZE)

    # ── Secure HTTP Headers & Resource Protection ──
    application.add_middleware(
        SecurityValidationMiddleware
    )  # Handles CSRF and Origin checks.
    application.add_middleware(SecurityHeadersMiddleware)  # Injects CSP, HSTS, etc.

    # ── CORS ──
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )

    return application


if __name__ == "__main__":
    create_app()
