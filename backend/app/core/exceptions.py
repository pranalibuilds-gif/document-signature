import traceback
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.core.logging import logger

async def global_exception_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, "request_id", "N/A")

    # Log the full traceback
    logger.error(
        f"Unhandled exception occurred: {exc}\n{traceback.format_exc()}",
        extra={"request_id": request_id}
    )

    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
        headers={"X-Request-ID": request_id}
    )

async def http_exception_handler(request: Request, exc: HTTPException):
    request_id = getattr(request.state, "request_id", "N/A")

    logger.warning(
        f"HTTP exception: {exc.status_code} {exc.detail} - Path: {request.url.path}",
        extra={"request_id": request_id}
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers={"X-Request-ID": request_id}
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    request_id = getattr(request.state, "request_id", "N/A")

    logger.warning(
        f"Validation error: {exc.errors()} - Path: {request.url.path}",
        extra={"request_id": request_id}
    )

    # Let FastAPI handle the actual response body for validation errors (usually 422)
    from fastapi.exception_handlers import request_validation_exception_handler
    response = await request_validation_exception_handler(request, exc)
    response.headers["X-Request-ID"] = request_id
    return response
