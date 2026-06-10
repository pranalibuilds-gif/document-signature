from fastapi import APIRouter
from app.modules.auth.router import router as auth_router
from app.modules.documents.router import router as documents_router
from app.modules.signers.router import router as signers_router
from app.modules.fields.router import router as fields_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(documents_router)
api_router.include_router(signers_router)
api_router.include_router(fields_router)
