"""Aggregates all feature routers under the v1 API namespace.

This module is the central registration point for the backend API. Each module
adds its own endpoints (auth, documents, signing, admin, etc.) here so the main
application can expose a single versioned entrypoint while keeping feature code
organized into separate domains.
"""

from fastapi import APIRouter
from app.modules.auth.router import router as auth_router
from app.modules.documents.router import router as documents_router
from app.modules.signers.router import router as signers_router
from app.modules.fields.router import router as fields_router
from app.modules.signing.router import router as signing_router
from app.modules.admin.router import router as admin_router
from app.modules.users.router import router as users_router

# Versioned API router: all feature routes are mounted here before the app
# is started in the root FastAPI entrypoint.
api_router = APIRouter()

# Router order is intentionally grouped by domain so auth and user flows are
# available before document and signing operations are mounted.
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(documents_router)
api_router.include_router(signers_router)
api_router.include_router(fields_router)
api_router.include_router(signing_router)
api_router.include_router(admin_router)
