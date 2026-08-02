"""Security headers middleware for application-level protection."""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Adds security headers to all responses.

    These complement Nginx-level headers and provide protection
    even if Nginx is bypassed.
    """

    HEADERS = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "SAMEORIGIN",
        "X-XSS-Protection": "1; mode=block",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "X-Permitted-Cross-Domain-Policies": "none",
    }

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        for key, value in self.HEADERS.items():
            response.headers[key] = value
        return response
