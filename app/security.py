"""Security utilities — IP anonymization, trusted origin check, headers middleware."""

from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response, JSONResponse
from fastapi import Request, status
from urllib.parse import urlparse
import unicodedata
import ipaddress
import secrets
import logging
import hmac
import re


from app.config import settings

logger = logging.getLogger(__name__)

def anonymize_ip(ip: str) -> str:
    """
    Mask the last octet of an IPv4 address or the last 80 bits of IPv6.

    Examples:
    192.168.1.42 → 192.168.1.0
    ::ffff:10.0.0.5 → ::ffff:10.0.0.0
    2001:db8::1 → 2001:db8::
    """
    try:
        addr = ipaddress.ip_address(ip)
        if isinstance(addr, ipaddress.IPv4Address):
            # Zero the last octet (/24 mask)
            network = ipaddress.IPv4Network(f"{ip}/24", strict=False)
            return str(network.network_address)
        else:
            # Zero the last 80 bits (/48 mask)
            network = ipaddress.IPv6Network(f"{ip}/48", strict=False)
            return str(network.network_address)
    except ValueError:
        # If it's not a valid IP (e.g. behind a proxy returning garbage),
        # return a safe placeholder instead of leaking the raw value.
        logger.warning(f"Could not parse IP for anonymization: {ip!r}")
        return "0.0.0.0"

def get_real_ip(request: Request) -> str:
    """Extract real user IP from Cloudflare or standard proxy headers."""
    # Priority: CF-Connecting-IP > X-Forwarded-For > remote_addr
    cf_ip = request.headers.get("CF-Connecting-IP")
    if cf_ip:
        return cf_ip
    
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        # Get the first IP in the list
        return forwarded.split(",")[0].strip()
    
    return request.client.host if request.client else "0.0.0.0"


def is_trusted_origin(request: Request) -> bool:
    """
    Validates request source (Origin/Referer) against ALLOWED_ORIGINS.
    Strict for state-changing methods; lenient for safe methods (GET/HEAD).
    """
    if "*" in settings.ALLOWED_ORIGINS: # ── Dev Support ─
        return True

    origin = request.headers.get("origin")
    referer = request.headers.get("referer")
    
    allowed = {o.rstrip("/") for o in settings.ALLOWED_ORIGINS}

    def _match(val: str | None, is_ref: bool = False) -> bool:
        if not val:
            return False
        if is_ref:
            p = urlparse(val)
            val = f"{p.scheme}://{p.netloc}"
        return val.rstrip("/") in allowed

    # State-changing MUST have a verified source
    if request.method in ("POST", "PUT", "DELETE", "PATCH"):
        return _match(origin) or _match(referer, is_ref=True)
    
    # Safe methods: GET, HEAD, OPTIONS
    if not origin and not referer:
        return True
    
    # Most likely from malicious site/source
    return _match(origin) or _match(referer, is_ref=True)


# ── Pre-compiled sanitization patterns (compiled once at import time) ──
_RE_ALLOWED = re.compile(r"[^\w\s\-./()'+,]")  # Allowlist: word chars, spaces, - . / ( ) ' + ,
_RE_WHITESPACE = re.compile(r"\s+")

_DEFAULT_MAX_LENGTH = 120


def validate_input(user_input: str | None, *, max_length: int = _DEFAULT_MAX_LENGTH) -> str:
    """
    Sanitize untrusted string input for safe storage and display.

    Pipeline (order matters):
        1. Unicode normalize (NFKC) — canonicalize before any byte-level ops.
        2. Strip control characters (Unicode category C*).
        3. Allowlist filter — keep only safe characters.
        4. Collapse whitespace and trim.
        5. Truncate to max_length — done last so we never slice mid-character.
    """
    if not user_input or not isinstance(user_input, str):
        return ""

    raw = user_input

    # Canonicalize Unicode (e.g., ﬁ → fi, ℃ → °C)
    cleaned = unicodedata.normalize("NFKC", raw)

    # Strip control characters (null bytes, RTL overrides, zero-width joiners, etc.)
    cleaned = "".join(ch for ch in cleaned if unicodedata.category(ch)[0] != "C")

    # Allowlist filter — permits word chars, whitespace, and: - . / ( ) ' + ,
    cleaned = _RE_ALLOWED.sub("", cleaned)

    # Collapse runs of whitespace into a single space
    cleaned = _RE_WHITESPACE.sub(" ", cleaned).strip()

    # Truncate AFTER normalization so we never split a multi-byte sequence
    cleaned = cleaned[:max_length]

    if cleaned != raw:
        logger.debug("validate_input: sanitized %r → %r", raw, cleaned)

    return cleaned


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Injects browser-security headers into every response:

    • X-Content-Type-Options – prevent MIME-sniffing
    • X-Frame-Options – prevent clickjacking
    • X-XSS-Protection – legacy XSS filter hint
    • Referrer-Policy – limit referrer leakage
    • Permissions-Policy – restrict browser APIs
    • Content-Security-Policy – restrict resource loading

    Respects development environment via settings.STRICT_SECURITY.
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Generate random nonce for this request (128-bit)
        nonce = secrets.token_urlsafe(16)
        request.state.csp_nonce = nonce

        # Generate CSRF token for cookie-based CSRF protection
        csrf_token = secrets.token_urlsafe(32)
        request.state.csrf_token = csrf_token

        response = await call_next(request)

        # Set CSRF cookie with secure flags
        # Note: httponly=False is required because JavaScript needs to read
        # the cookie to send as X-CSRF-Token header. This is the Double-Submit
        # Cookie pattern - cookie is auto-sent by browser, header must match.
        response.set_cookie(
            "csrf_token",
            value=csrf_token,
            secure=settings.STRICT_SECURITY,
            httponly=False,  # Required: JS needs to read for header
            samesite="strict",
            max_age=3_600,  # 1 hour
        )

        # ── Standard Security Headers (Applied always) ──
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=(), payment=()"
        )

        # ── CSP Configuration ──
        if request.url.path in ("/docs", "/redoc", "/openapi.json"):
            # Relaxed CSP for Swagger/ReDoc
            csp_parts = [
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net",
                "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net",
                "img-src 'self' data: https://fastapi.tiangolo.com",
            ]
        else:
            # Strict CSP for the rest of the app
            csp_parts = [
                # Fallback: only allow resources from our own domain (MUST be first)
                "default-src 'self'",
                # Trusted scripts: nonce for our own scripts, strict-dynamic so they
                # can load sub-scripts, and explicit Turnstile origin.
                f"script-src 'nonce-{nonce}' 'strict-dynamic' https://challenges.cloudflare.com",
                # Trusted styles via our domain or specific nonce
                f"style-src 'self' 'nonce-{nonce}'",
                # Allow images from our domain or base64 data: URIs and cloudflare
                "img-src 'self' data: https://challenges.cloudflare.com",
                # Restrict XHR/Fetch/WebSockets to ipgeo.myip.link and ourself
                "connect-src 'self' https://ipgeo.myip.link https://challenges.cloudflare.com",
                "form-action 'self'",  # Prevent form-data theft
                "font-src 'self'",  # Only allow fonts from our own domain
                "base-uri 'self'",  # Prevent <base> hijack
                "frame-ancestors 'none'",  # Prevent site from being framed (Clickjacking)
                "frame-src 'self' https://challenges.cloudflare.com",  # Allow Cloudflare Turnstile iframe
                "worker-src 'self' blob:",  # Turnstile may spawn workers
                "child-src 'self' https://challenges.cloudflare.com blob:",  # Turnstile child frames
                "object-src 'none'",  # Block plugins (Flash, etc.)
            ]

        # ── Environment Specific (Applied only in production) ──
        if settings.STRICT_SECURITY:
            # HSTS: Only HTTPS for 1 year (include subdomains)
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )

            # Only force HTTPS upgrades
            csp_parts.append("upgrade-insecure-requests")

        response.headers["Content-Security-Policy"] = "; ".join(csp_parts)

        return response


class SecurityValidationMiddleware(BaseHTTPMiddleware):
    """
    Middleware to validate state-changing requests (POST, PUT, DELETE, PATCH).
    Checks:
    1. is_trusted_origin – verifies Origin/Referer against ALLOWED_ORIGINS.
    2. CSRF token matching – compares 'csrf_token' cookie with 'X-CSRF-Token' header.
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Only validate state-changing methods
        if request.method in ("POST", "PUT", "DELETE", "PATCH"):
            # Skip validation for the Telegram Webhook (handled by its own secret check)
            if request.url.path == "/webhook":
                return await call_next(request)

            # Origin/Referer Validation
            if not is_trusted_origin(request):
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={
                        "error_code": "FP_ERR_AUTH",
                        "message": "Request not authorized (Untrusted Origin).",
                    },
                )

            # CSRF Validation
            csrf_cookie = request.cookies.get("csrf_token")
            csrf_header = request.headers.get("X-CSRF-Token")

            if not csrf_cookie or not csrf_header or not hmac.compare_digest(csrf_cookie, csrf_header):
                logger.warning(f"CSRF validation failed for {request.url.path}")
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={
                        "error_code": "FP_ERR_AUTH",
                        "message": "Request not authorized (CSRF Mismatch).",
                    },
                )

        return await call_next(request)
