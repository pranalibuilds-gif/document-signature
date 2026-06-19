"""
API endpoints for managing documents.
Handles creation, PDF uploads, activation, and status tracking.
"""
from fastapi import APIRouter, Depends, status, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.deps import get_db, get_current_user
from app.modules.users.models import User
from app.modules.documents.service import DocumentService
from app.modules.documents.schemas import DocumentCreate, DocumentUpdate, DocumentRead
from app.utils.storage import StorageService
from app.modules.audit.schemas import AuditLogRead
from app.modules.audit.repository import AuditRepository
import uuid

router = APIRouter(prefix="/documents", tags=["documents"])

@router.post("", response_model=DocumentRead, status_code=status.HTTP_201_CREATED)
async def create_document(
    doc_in: DocumentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Creates a new document entry in DRAFT state."""
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
    """
    Uploads the physical PDF file for a document.
    Replaces any existing file and handles storage logic.
    """
    import uuid
    service = DocumentService(db)
    doc_file = await service.upload_file(uuid.UUID(document_id), current_user.id, file)
    await db.commit()

    # If this was a replacement, delete the old file from disk
    if hasattr(doc_file, "_old_path_to_delete"):
        StorageService().delete_file(doc_file._old_path_to_delete)

    return {"message": "File uploaded successfully", "file_name": doc_file.file_name}

@router.get("/{document_id}/file")
async def download_document_file(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Returns the original uploaded PDF for viewing in the editor."""
    import uuid
    service = DocumentService(db)
    file_path = await service.get_document_file_path(uuid.UUID(document_id), current_user.id)
    return FileResponse(file_path, media_type="application/pdf")

@router.get("/{document_id}/final-file")
async def download_final_document(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Returns the generated PDF containing all captured signatures."""
    import uuid
    from fastapi import HTTPException
    from app.common.enums import DocumentStatus
    service = DocumentService(db)
    doc_id = uuid.UUID(document_id)

    document = await service.get_document(doc_id, current_user.id)
    if document.status != DocumentStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Document is not completed")

    final_file = await service.repo.get_final_file(doc_id)
    if not final_file:
        raise HTTPException(status_code=404, detail="Final PDF not generated yet")

    import os
    if not os.path.exists(final_file.file_path):
        raise HTTPException(status_code=404, detail="Physical file missing on server")

    return FileResponse(final_file.file_path, media_type="application/pdf")

@router.post("/{document_id}/activate", status_code=status.HTTP_200_OK)
async def activate_document(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Transitions document from DRAFT to PENDING.
    Generates secure signing links and notifies all assigned signers.
    """
    import uuid
    from app.common.enums import NotificationType
    service = DocumentService(db)
    doc_id = uuid.UUID(document_id)

    # Fetch document first to ensure existence
    document = await service.repo.get_by_id(doc_id)
    if not document:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Document not found")

    # 1. Update state in database
    await service.activate_document(doc_id, current_user.id)
    await db.commit()

    # 2. Post-commit: Send out the invitation emails
    if hasattr(document, "_invitation_data"):
        for signer, raw_token in document._invitation_data:
            link = f"http://localhost:3000/signing/{raw_token}/welcome"
            await service.notification_service.send_notification(
                recipient_email=signer.email,
                subject=f"Signature Required: {document.title}",
                body=f"You have been invited to sign '{document.title}'. Use this link: {link}",
                type=NotificationType.INVITATION,
                document_id=doc_id
            )

    return {"message": "Document activated and invitations sent"}

@router.get("/{document_id}/audit", response_model=list[AuditLogRead])
async def get_document_audit(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Returns the audit trail for a specific document, accessible to the owner."""
    service = DocumentService(db)
    doc_id = uuid.UUID(document_id)

    # Check ownership
    await service.get_document(doc_id, current_user.id)

    repo = AuditRepository(db)
    return await repo.list_by_document(doc_id)

@router.get("", response_model=list[DocumentRead])
async def list_documents(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lists all documents owned by the current user."""
    service = DocumentService(db)
    return await service.list_documents(current_user.id, skip, limit)

@router.get("/{document_id}", response_model=DocumentRead)
async def get_document(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Fetches full metadata for a specific document."""
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
    """Updates document metadata (e.g., title)."""
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
    """Performs a soft-delete of a document."""
    import uuid
    service = DocumentService(db)
    await service.delete_document(uuid.UUID(document_id), current_user.id)
    await db.commit()
