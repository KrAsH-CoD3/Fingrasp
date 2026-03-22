"""Security utilities — IP anonymization, trusted origin check, headers middleware."""

from __future__ import annotations
from urllib.parse import urlparse
import ipaddress
import secrets
import logging

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response
from fastapi import Request

from app.config import settings

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# 1. IP Anonymization
# ─────────────────────────────────────────────


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


# ─────────────────────────────────────────────
# 2. Trusted Origin Check
# ─────────────────────────────────────────────


def is_trusted_origin(request: Request) -> bool:
    """
    Strict Origin/Referer validation.
    For state-changing methods (POST, PUT, DELETE, PATCH), requires Origin header
    or validates Referer against allowed origins.
    GET/HEAD requests may pass without origin if they have no side effects.
    """

    origin = request.headers.get("origin")
    referer = request.headers.get("referer")

    # For state-changing methods, Origin header is REQUIRED
    if request.method in ("POST", "PUT", "DELETE", "PATCH"):
        if origin:
            # Validate Origin header against allowed list
            if origin.rstrip("/") in [o.rstrip("/") for o in settings.ALLOWED_ORIGINS]:
                return True
            logger.warning(f"Blocked request from untrusted origin: {origin}")
            return False
        elif referer:
            # Fall back to Referer validation
            parsed = urlparse(referer)
            ref_origin = f"{parsed.scheme}://{parsed.netloc}".rstrip("/")
            if ref_origin in [o.rstrip("/") for o in settings.ALLOWED_ORIGINS]:
                return True
            logger.warning(f"Blocked request with untrusted referer: {referer}")
            return False
        else:
            # No Origin/Referer - reject state-changing requests
            logger.warning(
                f"Blocked {request.method} request without Origin or Referer headers"
            )
            return False

    # For safe methods (GET, HEAD, etc.), allow missing Origin/Referer
    if origin:
        return origin.rstrip("/") in [o.rstrip("/") for o in settings.ALLOWED_ORIGINS]
    elif referer:
        parsed = urlparse(referer)
        ref_origin = f"{parsed.scheme}://{parsed.netloc}".rstrip("/")
        return ref_origin in [o.rstrip("/") for o in settings.ALLOWED_ORIGINS]
    else:
        # Safe methods without origin/referer are allowed (same-origin navigation)
        return True


# ─────────────────────────────────────────────
# 3. Secure HTTP Headers Middleware
# ─────────────────────────────────────────────


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
                # Trusted scripts via nonce or dynamic loading
                f"script-src 'nonce-{nonce}' 'strict-dynamic'",
                # Trusted styles via our domain or specific nonce
                f"style-src 'self' 'nonce-{nonce}'",
                # Allow images from our domain or base64 data: URIs
                "img-src 'self' data:",
                # Restrict XHR/Fetch/WebSockets to ipgeo.myip.link and ourself
                "connect-src 'self' https://ipgeo.myip.link",
                "form-action 'self'",  # Prevent form-data theft
                "font-src 'self'",  # Only allow fonts from our own domain
                "base-uri 'self'",  # Prevent <base> hijack
                "frame-ancestors 'none'",  # Prevent site from being framed (Clickjacking)
                "object-src 'none'",  # Block plugins (Flash, etc.)
            ]

            # Add CSP reporting endpoint in production to detect violations
            if settings.STRICT_SECURITY:
                csp_parts.append("report-uri /csp-report")

        # ── Environment Specific (Applied only in production) ──
        if settings.STRICT_SECURITY:
            # HSTS: Only HTTPS for 1 year (include subdomains)
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )

            # Only force HTTPS upgrades
            csp_parts.append("upgrade-insecure-requests")

        # Fallback: only allow resources from our own domain
        csp_parts.append("default-src 'self'")
        response.headers["Content-Security-Policy"] = "; ".join(csp_parts)

        return response
