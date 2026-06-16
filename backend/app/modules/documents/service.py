"""
Service layer for Document management.
Orchestrates the lifecycle of a document: Draft -> Active -> Signed -> Final PDF.
"""
import uuid
import hashlib
import secrets
from datetime import datetime, timezone, timedelta
from fastapi import HTTPException, status, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.documents.models import Document, DocumentFile
from app.modules.documents.repository import DocumentRepository
from app.modules.documents.schemas import DocumentCreate
from app.modules.signers.models import SigningToken
from app.modules.signers.repository import SignerRepository
from app.modules.users.repository import UserRepository
from app.modules.notifications.service import NotificationService
from app.modules.audit.service import AuditService
from app.common.enums import DocumentStatus, SignerStatus, AuditActorType, AuditEventType, NotificationType
from app.utils.storage import StorageService
from app.core.config import settings
from app.core.logging import logger

class DocumentService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = DocumentRepository(session)
        self.audit_service = AuditService(session)
        self.storage = StorageService()
        self.signer_repo = SignerRepository(session)
        self.user_repo = UserRepository(session)
        self.notification_service = NotificationService(session)

    async def _get_field_service(self):
        """Lazy load FieldService to avoid circular imports."""
        from app.modules.fields.service import FieldService
        return FieldService(self.session)

    async def create_document(self, owner_id: uuid.UUID, doc_in: DocumentCreate) -> Document:
        """Initializes a new document record in DRAFT status."""
        document = Document(
            owner_id=owner_id,
            **doc_in.model_dump(),
            status=DocumentStatus.DRAFT
        )
        created_doc = await self.repo.create(document)
        logger.info(f"Document created: {created_doc.id}")

        await self.audit_service.record_event(
            event_type=AuditEventType.DOCUMENT_CREATED,
            actor_type=AuditActorType.USER,
            user_id=owner_id,
            document_id=created_doc.id,
            event_data={"title": created_doc.title}
        )
        return created_doc

    async def activate_document(self, document_id: uuid.UUID, user_id: uuid.UUID) -> dict:
        """
        Finalizes document setup and makes it available for signers.
        Validates readiness, generates unique signing tokens, and updates status.
        """
        # 1. Access Control: Ensure owner is verified
        document = await self.get_document(document_id, user_id)
        owner = await self.user_repo.get_by_id(user_id)

        if not owner or not owner.is_verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Email verification required to activate documents"
            )

        if document.status != DocumentStatus.DRAFT:
            raise HTTPException(status_code=409, detail="Only draft documents can be activated")

        # 2. Field Validation: Check if every signer has at least one field
        field_service = await self._get_field_service()
        is_ready = await field_service.validate_document_ready_for_signing(document_id, user_id)
        if not is_ready:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Document not ready. Ensure PDF is uploaded and all signers have fields."
            )

        # 3. Security: Generate secure, single-use signing links for each signer
        signers = await self.signer_repo.list_by_document(document_id)
        token_data = []

        for signer in signers:
            raw_token = secrets.token_urlsafe(32)
            token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
            expires_at = datetime.now(timezone.utc) + timedelta(days=settings.SIGNING_TOKEN_EXPIRY_DAYS)

            db_token = SigningToken(
                document_signer_id=signer.id,
                token_hash=token_hash,
                expires_at=expires_at
            )
            await self.signer_repo.create_token(db_token)
            token_data.append((signer, raw_token)) # Used by router to send emails

        # 4. Status Transition
        document.status = DocumentStatus.PENDING
        await self.repo.update(document)

        # 5. Audit: Log that invitations were triggered
        await self.audit_service.record_event(
            event_type=AuditEventType.INVITATION_SENT,
            actor_type=AuditActorType.USER,
            user_id=user_id,
            document_id=document_id,
            event_data={"signer_count": len(signers)}
        )

        # Return token list to router for email delivery
        document._invitation_data = token_data
        return {"message": "Document activated"}

    async def evaluate_document_status(self, document_id: uuid.UUID) -> None:
        """
        State Machine: Re-calculates document status based on collective signer actions.
        Triggered after every successful signature or rejection.
        """
        document = await self.repo.get_by_id(document_id)
        if not document or document.status in [DocumentStatus.COMPLETED, DocumentStatus.REJECTED]:
            return

        signers = await self.signer_repo.list_by_document(document_id)
        if not signers:
            return

        all_signed = all(s.status == SignerStatus.SIGNED for s in signers)
        any_rejected = any(s.status == SignerStatus.REJECTED for s in signers)
        any_signed = any(s.status == SignerStatus.SIGNED for s in signers)

        # --- REJECTION LOGIC ---
        if any_rejected:
            document.status = DocumentStatus.REJECTED
            document.rejected_at = datetime.now(timezone.utc)
            await self.repo.update(document)

            # Find the signer who rejected to log it
            rejected_signer = next(s for s in signers if s.status == SignerStatus.REJECTED)
            await self.audit_service.record_event(
                event_type=AuditEventType.DOCUMENT_REJECTED,
                actor_type=AuditActorType.SYSTEM,
                document_id=document_id,
                event_data={"signer": rejected_signer.email, "reason": rejected_signer.rejection_reason}
            )

        # --- COMPLETION LOGIC ---
        elif all_signed:
            document.status = DocumentStatus.COMPLETED
            document.completed_at = datetime.now(timezone.utc)
            await self.repo.update(document)

            await self.audit_service.record_event(
                event_type=AuditEventType.DOCUMENT_COMPLETED,
                actor_type=AuditActorType.SYSTEM,
                document_id=document_id
            )

            # Notify Owner
            owner = await self.user_repo.get_by_id(document.owner_id)
            if owner:
                await self.notification_service.send_notification(
                    recipient_email=owner.email,
                    subject=f"Document Completed: {document.title}",
                    body=f"All signers have signed '{document.title}'. You can now download the finalized document.",
                    type=NotificationType.COMPLETION,
                    document_id=document_id
                )

            # Trigger background PDF generation with actual signature overlays
            from app.modules.documents.pdf_service import PdfGenerationService
            pdf_service = PdfGenerationService(self.session)
            await pdf_service.generate_final_pdf(document_id)

        # --- PARTIAL LOGIC ---
        elif any_signed and document.status == DocumentStatus.PENDING:
            document.status = DocumentStatus.PARTIALLY_SIGNED
            await self.repo.update(document)

    async def upload_file(
        self, document_id: uuid.UUID, user_id: uuid.UUID, file: UploadFile
    ) -> DocumentFile:
        """
        Validates and saves the original PDF file to disk.
        Ensures document is still a DRAFT before allowing upload.
        """
        document = await self.get_document(document_id, user_id)

        if document.status != DocumentStatus.DRAFT:
            raise HTTPException(status_code=409, detail="Cannot change files after activation")

        if file.content_type != "application/pdf":
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")

        # TC-7.4.3 Size Limit enforcement
        if file.size and file.size > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Maximum allowed size is {settings.MAX_UPLOAD_SIZE_MB}MB"
            )

        # Handle existing file replacement
        old_file = await self.repo.get_original_file(document_id)

        # Generate unique storage name to prevent collisions
        stored_name = f"{uuid.uuid4()}.pdf"
        file_path = await self.storage.save_file(file, stored_name)

        doc_file = DocumentFile(
            document_id=document_id,
            file_name=file.filename,
            stored_name=stored_name,
            file_path=file_path,
            file_size=file.size,
            mime_type=file.content_type,
            is_final=False
        )
        created_file = await self.repo.create_file(doc_file)

        # Mark old file for deletion after DB commit
        if old_file:
            await self.repo.delete_file_record(old_file.id)
            created_file._old_path_to_delete = old_file.file_path

        return created_file

    async def get_document(self, document_id: uuid.UUID, user_id: uuid.UUID) -> Document:
        """Utility to fetch a document while enforcing ownership security."""
        document = await self.repo.get_by_id(document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        if document.owner_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        return document

    async def list_documents(self, owner_id: uuid.UUID, skip: int = 0, limit: int = 100) -> list[Document]:
        """Returns a list of documents owned by the specified user."""
        return await self.repo.list_by_owner(owner_id, skip, limit)

    async def update_document(
        self, document_id: uuid.UUID, user_id: uuid.UUID, doc_in: DocumentUpdate
    ) -> Document:
        """Updates document metadata while enforcing ownership and state rules."""
        document = await self.get_document(document_id, user_id)

        # State Protection: Only DRAFT documents can be edited
        if document.status != DocumentStatus.DRAFT:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Cannot edit document in {document.status} state"
            )

        update_data = doc_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(document, key, value)

        return await self.repo.update(document)

    async def delete_document(self, document_id: uuid.UUID, user_id: uuid.UUID) -> None:
        """Performs a deletion of a document after checking ownership."""
        await self.get_document(document_id, user_id)
        await self.repo.delete(document_id)

    async def get_document_file_path(self, document_id: uuid.UUID, user_id: uuid.UUID) -> str:
        """Returns the physical file path for a document, enforcing ownership."""
        await self.get_document(document_id, user_id)
        original_file = await self.repo.get_original_file(document_id)
        if not original_file:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document file not found")
        return original_file.file_path
