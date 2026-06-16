"""
Entry point for the FastAPI application.
Handles application lifespan, middleware configuration, and router aggregation.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from app.core.config import settings
from app.api.api_v1 import api_router
from app.jobs.scheduler import start_scheduler, stop_scheduler
from app.core.middleware.request_id import RequestIdMiddleware
from app.core.middleware.security import SecurityHeadersMiddleware
from app.core.exceptions import global_exception_handler, http_exception_handler, validation_exception_handler
from app.core.logging import logger
from app.core.rate_limit import limiter
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages the application startup and shutdown events.
    Starts background jobs (scheduler) on startup and stops them on shutdown.
    """
    # Startup: Initialize resources
    logger.info("Application starting up...")
    start_scheduler()

    yield # Application runs here

    # Shutdown: Clean up resources
    logger.info("Application shutting down...")
    stop_scheduler()

# Initialize FastAPI app with project metadata
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    debug=settings.DEBUG,
    lifespan=lifespan,
)

# --- Middleware Configuration ---
app.state.limiter = limiter # Attach rate limiter to app state
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(RequestIdMiddleware) # Trace every request with a unique ID
app.add_middleware(SecurityHeadersMiddleware) # Add hardening security headers

# --- Global Exception Handlers ---
# Ensures consistent JSON error responses for all failure types
app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

# --- Router Registration ---
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/health")
async def health_check():
    """Basic health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT
    }

@app.get("/debug-error")
async def trigger_error():
    """Testing endpoint to verify that errors are logged and handled correctly."""
    raise Exception("Test exception for logging verification")
