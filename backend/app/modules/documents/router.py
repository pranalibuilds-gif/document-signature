from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.deps import get_db, get_current_user
from app.modules.users.models import User
from app.modules.documents.service import DocumentService
from app.modules.documents.schemas import DocumentCreate, DocumentUpdate, DocumentRead

router = APIRouter(prefix="/documents", tags=["documents"])

@router.post("", response_model=DocumentRead, status_code=status.HTTP_201_CREATED)
async def create_document(
    doc_in: DocumentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = DocumentService(db)
    document = await service.create_document(current_user.id, doc_in)
    await db.commit()
    return document

@router.get("", response_model=list[DocumentRead])
async def list_documents(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = DocumentService(db)
    return await service.list_documents(current_user.id, skip, limit)

@router.get("/{document_id}", response_model=DocumentRead)
async def get_document(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    import uuid
    service = DocumentService(db)
    return await service.get_document(uuid.UUID(document_id), current_user.id)

@router.patch("/{document_id}", response_model=DocumentRead)
async def update_document(
    document_id: str,
    doc_in: DocumentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    import uuid
    service = DocumentService(db)
    document = await service.update_document(uuid.UUID(document_id), current_user.id, doc_in)
    await db.commit()
    return document

@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    import uuid
    service = DocumentService(db)
    await service.delete_document(uuid.UUID(document_id), current_user.id)
    await db.commit()
