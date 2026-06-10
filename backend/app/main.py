from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from app.core.config import settings
from app.api.api_v1 import api_router
from app.jobs.scheduler import start_scheduler, stop_scheduler
from app.core.middleware.request_id import RequestIdMiddleware
from app.core.exceptions import global_exception_handler, http_exception_handler, validation_exception_handler
from app.core.logging import logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Application starting up...")
    start_scheduler()
    yield
    # Shutdown
    logger.info("Application shutting down...")
    stop_scheduler()

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    debug=settings.DEBUG,
    lifespan=lifespan,
)

# Middleware
app.add_middleware(RequestIdMiddleware)

# Exception Handlers
app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/debug-error")
async def trigger_error():
    """Endpoint to test global exception handling"""
    raise Exception("Test exception for logging verification")
