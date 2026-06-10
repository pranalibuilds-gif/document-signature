from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.deps import get_db
from app.modules.signing.service import SigningService
from app.modules.signing.schemas import SigningSessionRead, SigningSubmission, RejectionRequest
from app.core.rate_limit import limiter
from fastapi import Request

router = APIRouter(prefix="/signing", tags=["signing"])

@router.get("/{token}", response_model=SigningSessionRead)
@limiter.limit("20/minute")
async def get_signing_session(
    request: Request,
    token: str,
    db: AsyncSession = Depends(get_db)
):
    service = SigningService(db)
    return await service.get_signer_document(token)

@router.post("/{token}/submit", status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
async def submit_signing(
    request: Request,
    token: str,
    submission: SigningSubmission,
    db: AsyncSession = Depends(get_db)
):
    service = SigningService(db)
    await service.submit_signature(token, submission)
    await db.commit()
    return {"message": "Signature submitted successfully"}

@router.post("/{token}/reject", status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
async def reject_document(
    request: Request,
    token: str,
    rejection: RejectionRequest,
    db: AsyncSession = Depends(get_db)
):
    service = SigningService(db)
    await service.reject_document(token, rejection)
    await db.commit()
    return {"message": "Document rejected successfully"}
