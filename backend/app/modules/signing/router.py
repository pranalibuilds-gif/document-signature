from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.deps import get_db
from app.modules.signing.service import SigningService
from app.modules.signing.schemas import SigningSessionRead, SigningSubmission

router = APIRouter(prefix="/signing", tags=["signing"])

@router.get("/{token}", response_model=SigningSessionRead)
async def get_signing_session(
    token: str,
    db: AsyncSession = Depends(get_db)
):
    service = SigningService(db)
    return await service.get_signer_document(token)

@router.post("/{token}/submit", status_code=status.HTTP_200_OK)
async def submit_signing(
    token: str,
    submission: SigningSubmission,
    db: AsyncSession = Depends(get_db)
):
    service = SigningService(db)
    await service.submit_signature(token, submission)
    await db.commit()
    return {"message": "Signature submitted successfully"}
