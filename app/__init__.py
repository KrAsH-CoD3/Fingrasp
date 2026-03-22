from starlette.types import ASGIApp, Receive, Scope, Send
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from starlette.responses import Response
from fastapi import FastAPI, Request

from app.routes.fingerprint import router as fingerprint_router
from app.config import settings, MAX_REQUEST_BODY_SIZE
from app.security import SecurityHeadersMiddleware
from app.database import setup_db
from app.limiter import limiter


class BodySizeLimitMiddleware:
    """Middleware to limit request body size before JSON parsing."""

    def __init__(self, app: ASGIApp, max_size: int):
        self.app = app
        self.max_size = max_size

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Only limit body size for POST/PUT/PATCH requests
        method = scope.get("method", "GET")
        if method in ("GET", "HEAD", "OPTIONS", "DELETE"):
            await self.app(scope, receive, send)
            return

        # Read the body first to check size
        body_size = 0
        body_parts = []

        async def read_body() -> bytes:
            nonlocal body_size
            while True:
                message = await receive()
                if message.get("type") == "http.request":
                    chunk = message.get("body", b"")
                    body_size += len(chunk)
                    if body_size > self.max_size:
                        # Body too large, reject immediately
                        response = Response(
                            content=f'{{"detail": "Request body exceeds maximum size"}}',
                            status_code=413,
                            headers={"Content-Type": "application/json"},
                        )
                        await response(scope, receive, send)
                        return None  # Signal rejection
                    body_parts.append(chunk)
                    if not message.get("more_body", False):
                        break
                else:
                    break
            return b"".join(body_parts)

        full_body = await read_body()
        if full_body is None:
            return  # Rejected due to size

        # Create new receive function that returns the cached body
        async def cached_receive():
            if cached_receive.called:
                return {"type": "http.request", "body": b"", "more_body": False}
            cached_receive.called = True
            return {"type": "http.request", "body": full_body, "more_body": False}

        cached_receive.called = False

        await self.app(scope, cached_receive, send)


class RateLimitedStaticFiles(StaticFiles):
    """StaticFiles wrapper with rate limiting support."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._rate_limits = {}
        self._rate_limit_lock = False

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request = Request(scope)
            # Apply rate limit: 20 requests per minute for static files
            from slowapi.util import get_remote_address
            import time

            key = f"static:{get_remote_address(request)}"

            now = time.time()
            window_start = now - 60  # 60 second window

            # Cleanup old entries periodically to prevent memory growth
            # Every 100 requests, remove entries for IPs with no recent activity
            if len(self._rate_limits) % 100 == 0:
                self._cleanup_old_entries(now, window_start)

            # Get or create rate limit entry
            if key not in self._rate_limits:
                self._rate_limits[key] = []

            # Filter to only keep timestamps within the window
            self._rate_limits[key] = [
                ts for ts in self._rate_limits[key] if ts > window_start
            ]

            # Check if over limit (20 requests per minute)
            if len(self._rate_limits[key]) >= 20:
                response = Response(
                    content="Rate limit exceeded",
                    status_code=429,
                    headers={"Retry-After": "60"},
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
async def lifespan(app: FastAPI):
    client, db = setup_db()
    app.state.db = db

    yield
    client.close()


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

    # ── Request Body Size Limit ──
    # Added last among middlewares so it is outermost in the ASGI stack,
    # rejecting oversized payloads before any other middleware processes them.
    application.add_middleware(BodySizeLimitMiddleware, max_size=MAX_REQUEST_BODY_SIZE)

    # ── Secure HTTP Headers ──
    application.add_middleware(SecurityHeadersMiddleware)

    # ── CORS ──
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )

    return application
