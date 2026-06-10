import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.deps import get_db, get_current_user
from app.modules.users.models import User
from app.modules.signers.service import SignerService
from app.modules.signers.schemas import SignerCreate, SignerRead

router = APIRouter(prefix="/documents", tags=["signers"])

@router.post("/{document_id}/signers", response_model=SignerRead, status_code=status.HTTP_201_CREATED)
async def add_signer(
    document_id: str,
    signer_in: SignerCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = SignerService(db)
    signer = await service.add_signer(uuid.UUID(document_id), current_user.id, signer_in)
    await db.commit()
    return signer

@router.get("/{document_id}/signers", response_model=list[SignerRead])
async def list_signers(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = SignerService(db)
    return await service.list_signers(uuid.UUID(document_id), current_user.id)

@router.delete("/{document_id}/signers/{signer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_signer(
    document_id: str,
    signer_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = SignerService(db)
    await service.remove_signer(uuid.UUID(document_id), current_user.id, uuid.UUID(signer_id))
    await db.commit()
