import uuid
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logging import logger

class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        start_time = time.time()

        # Log the incoming request
        logger.info(
            f"Incoming request: {request.method} {request.url.path}",
            extra={"request_id": request_id}
        )

        response = await call_next(request)

        process_time = (time.time() - start_time) * 1000
        formatted_process_time = "{0:.2f}".format(process_time)

        # Add Request ID to response headers
        response.headers["X-Request-ID"] = request_id

        # Log the response
        logger.info(
            f"Completed request: {request.method} {request.url.path} - Status: {response.status_code} - Duration: {formatted_process_time}ms",
            extra={"request_id": request_id}
        )

        return response
