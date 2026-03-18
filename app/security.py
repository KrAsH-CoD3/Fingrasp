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
        192.168.1.42   →  192.168.1.0
        ::ffff:10.0.0.5 →  ::ffff:10.0.0.0
        2001:db8::1     →  2001:db8::
    """
    try:
        addr = ipaddress.ip_address(ip)
        if isinstance(addr, ipaddress.IPv4Address):
            # Zero the last octet  (/24 mask)
            network = ipaddress.IPv4Network(f"{ip}/24", strict=False)
            return str(network.network_address)
        else:
            # Zero the last 80 bits  (/48 mask)
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
    Return True if the request's Origin or Referer header
    matches one of the configured ALLOWED_ORIGINS.

    Returns True when neither header is present (same-origin
    navigational requests from forms / fetch without Origin).
    """
    origin = request.headers.get("origin")
    referer = request.headers.get("referer")

    # If the browser sent an Origin header, check it
    if origin:
        return origin.rstrip("/") in [o.rstrip("/") for o in settings.ALLOWED_ORIGINS]

    # Fall back to Referer
    if referer:
        parsed = urlparse(referer)
        ref_origin = f"{parsed.scheme}://{parsed.netloc}".rstrip("/")
        return ref_origin in [o.rstrip("/") for o in settings.ALLOWED_ORIGINS]

    # No origin/referer — likely a same-origin request or server-to-server
    return True


# ─────────────────────────────────────────────
# 3. Secure HTTP Headers Middleware
# ─────────────────────────────────────────────

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Injects browser-security headers into every response:

    • X-Content-Type-Options    – prevent MIME-sniffing
    • X-Frame-Options           – prevent clickjacking
    • X-XSS-Protection          – legacy XSS filter hint
    • Referrer-Policy           – limit referrer leakage
    • Permissions-Policy        – restrict browser APIs
    • Content-Security-Policy   – restrict resource loading

    Respects development environment via settings.STRICT_SECURITY.
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Generate random nonce for this request (128-bit)
        nonce = secrets.token_urlsafe(16)
        request.state.csp_nonce = nonce

        response = await call_next(request)

        # ── Standard Security Headers (Applied always) ──
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=(), payment=()"
        )

        # ── CSP Configuration ──
        csp_parts = [
            "default-src 'self'",                                  # Fallback: only allow resources from our own domain
            f"script-src 'self' 'nonce-{nonce}' 'strict-dynamic'", # Trusted scripts via nonce or dynamic loading
            f"style-src 'self' 'nonce-{nonce}'",                   # Trusted styles via our domain or specific nonce
            "img-src 'self' data:",                                # Allow images from our domain or base64 data: URIs
            "connect-src 'self'",                                  # Restrict XHR/Fetch/WebSockets to our own domain
            "form-action 'self'",                                  # Prevent form-data theft
            "font-src 'self'",                                     # Only allow fonts from our own domain
            "base-uri 'self'",                                     # Prevent <base> hijack
            "frame-ancestors 'none'",                              # Prevent site from being framed (Clickjacking)
            "object-src 'none'",                                   # Block plugins (Flash, etc.)
        ]

        # ── Environment Specific (Applied only in production) ──
        if settings.STRICT_SECURITY:
            # HSTS: Only HTTPS for 1 year (include subdomains)
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
            # Only force HTTPS upgrades
            csp_parts.append("upgrade-insecure-requests")

        response.headers["Content-Security-Policy"] = "; ".join(csp_parts)

        # ── Server Disclosure ──
        # Hide the exact server version (some proxy servers might put it back)
        if "Server" in response.headers:
            del response.headers["Server"]

        return response
