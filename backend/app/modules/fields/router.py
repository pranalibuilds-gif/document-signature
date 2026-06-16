import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.deps import get_db, get_current_user
from app.modules.users.models import User
from app.modules.fields.service import FieldService
from app.modules.fields.schemas import SignatureFieldCreate, SignatureFieldRead, SignatureFieldUpdate

router = APIRouter(prefix="/documents", tags=["fields"])

@router.post("/{document_id}/fields", response_model=SignatureFieldRead, status_code=status.HTTP_201_CREATED)
async def add_field(
    document_id: str,
    field_in: SignatureFieldCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = FieldService(db)
    field = await service.add_field(uuid.UUID(document_id), current_user.id, field_in)
    await db.commit()
    return field

@router.get("/{document_id}/fields", response_model=list[SignatureFieldRead])
async def list_fields(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = FieldService(db)
    return await service.list_fields(uuid.UUID(document_id), current_user.id)

@router.patch("/{document_id}/fields/{field_id}", response_model=SignatureFieldRead)
async def update_field(
    document_id: str,
    field_id: str,
    field_in: SignatureFieldUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = FieldService(db)
    field = await service.update_field(
        uuid.UUID(document_id), current_user.id, uuid.UUID(field_id), field_in
    )
    await db.commit()
    return field

@router.delete("/{document_id}/fields/{field_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_field(
    document_id: str,
    field_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = FieldService(db)
    await service.remove_field(uuid.UUID(document_id), current_user.id, uuid.UUID(field_id))
    await db.commit()
