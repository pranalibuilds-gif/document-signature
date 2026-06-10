from fastapi import APIRouter, Depends, status, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.deps import get_db, get_current_user
from app.modules.users.models import User
from app.modules.documents.service import DocumentService
from app.modules.documents.schemas import DocumentCreate, DocumentUpdate, DocumentRead
from app.utils.storage import StorageService

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

@router.post("/{document_id}/upload", status_code=status.HTTP_200_OK)
async def upload_document_file(
    document_id: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    import uuid
    service = DocumentService(db)
    doc_file = await service.upload_file(uuid.UUID(document_id), current_user.id, file)
    await db.commit()

    # Post-commit cleanup of old physical file
    if hasattr(doc_file, "_old_path_to_delete"):
        StorageService().delete_file(doc_file._old_path_to_delete)

    return {"message": "File uploaded successfully", "file_name": doc_file.file_name}

@router.get("/{document_id}/file")
async def download_document_file(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    import uuid
    service = DocumentService(db)
    file_path = await service.get_document_file_path(uuid.UUID(document_id), current_user.id)
    return FileResponse(file_path, media_type="application/pdf")

@router.post("/{document_id}/activate", status_code=status.HTTP_200_OK)
async def activate_document(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    import uuid
    from app.common.enums import NotificationType
    service = DocumentService(db)
    doc_id = uuid.UUID(document_id)

    # 1. Activate (DB Changes)
    # We need the document object to get invitation data
    document = await service.repo.get_by_id(doc_id)
    if not document:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Document not found")

    await service.activate_document(doc_id, current_user.id)
    await db.commit()

    # 2. Send Notifications (Post-Commit)
    # Note: Service attached _invitation_data to the document instance
    if hasattr(document, "_invitation_data"):
        for signer, raw_token in document._invitation_data:
            # Construct link (Base URL would normally come from config)
            link = f"http://localhost:3000/signing/{raw_token}"
            await service.notification_service.send_notification(
                recipient_email=signer.email,
                subject=f"Signature Required: {document.title}",
                body=f"You have been invited to sign '{document.title}'. Use this link: {link}",
                type=NotificationType.INVITATION,
                document_id=doc_id
            )

    return {"message": "Document activated and invitations sent"}

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
