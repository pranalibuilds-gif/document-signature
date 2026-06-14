from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to every response.
    Protects against common web vulnerabilities like XSS, Clickjacking, and MIME-sniffing.
    """
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)

        # Prevent the browser from interpreting files as a different MIME type than what is specified
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Protect against clickjacking by preventing the app from being rendered in an iframe
        response.headers["X-Frame-Options"] = "DENY"

        # Enable Browser XSS filtering
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Control how much information is shared in the Referer header
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Basic Content Security Policy
        # In a real production app, this would be more restrictive based on frontend needs
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
            "font-src 'self' data:;"
        )

        return response
