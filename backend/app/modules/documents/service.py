import uuid
import hashlib
import secrets
from datetime import datetime, timezone, timedelta
from fastapi import HTTPException, status, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.documents.models import Document, DocumentFile
from app.modules.documents.repository import DocumentRepository
from app.modules.documents.schemas import DocumentCreate, DocumentUpdate
from app.modules.signers.models import SigningToken
from app.modules.signers.repository import SignerRepository
from app.modules.users.repository import UserRepository
from app.modules.notifications.service import NotificationService
from app.modules.audit.service import AuditService
from app.common.enums import DocumentStatus, SignerStatus, AuditActorType, AuditEventType, NotificationType
from app.utils.storage import StorageService
from app.core.config import settings

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
        from app.modules.fields.service import FieldService
        return FieldService(self.session)

    async def create_document(self, owner_id: uuid.UUID, doc_in: DocumentCreate) -> Document:
        document = Document(
            owner_id=owner_id,
            **doc_in.model_dump(),
            status=DocumentStatus.DRAFT
        )
        created_doc = await self.repo.create(document)

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
        Transitions document from DRAFT to PENDING.
        Generates tokens and prepares notifications.
        """
        # 1. Validate ownership and DRAFT status
        document = await self.get_document(document_id, user_id)
        if document.status != DocumentStatus.DRAFT:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Only draft documents can be activated"
            )

        # 2. Readiness Validation
        field_service = await self._get_field_service()
        is_ready = await field_service.validate_document_ready_for_signing(document_id, user_id)
        if not is_ready:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Document is not ready for signing. Ensure PDF is uploaded and every signer has fields assigned."
            )

        # 3. Generate Tokens
        signers = await self.signer_repo.list_by_document(document_id)
        token_data = [] # List of (signer, raw_token) to send emails after commit

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
            token_data.append((signer, raw_token))

        # 4. Update Status
        document.status = DocumentStatus.PENDING
        await self.repo.update(document)

        # 5. Audit
        await self.audit_service.record_event(
            event_type=AuditEventType.INVITATION_SENT, # Initial activation marks invitation process start
            actor_type=AuditActorType.USER,
            user_id=user_id,
            document_id=document_id,
            event_data={"signer_count": len(signers)}
        )

        # Attach token_data to the document object temporarily for the router to handle notifications
        document._invitation_data = token_data

        return {"message": "Document activated and invitations queued"}

    async def evaluate_document_status(self, document_id: uuid.UUID) -> None:
        """
        Re-evaluates document status based on signer actions.
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

        owner = await self.user_repo.get_by_id(document.owner_id)
        owner_email = owner.email if owner else "Unknown"

        if any_rejected:
            document.status = DocumentStatus.REJECTED
            document.rejected_at = datetime.now(timezone.utc)
            await self.repo.update(document)

            # Audit
            rejected_signer = next(s for s in signers if s.status == SignerStatus.REJECTED)
            await self.audit_service.record_event(
                event_type=AuditEventType.DOCUMENT_REJECTED,
                actor_type=AuditActorType.SYSTEM,
                document_id=document_id,
                event_data={"signer_email": rejected_signer.email}
            )

            # Notify Owner
            await self.notification_service.send_notification(
                recipient_email=owner_email,
                subject=f"Document Rejected: {document.title}",
                body=f"Signer {rejected_signer.email} has rejected '{document.title}'. Reason: {rejected_signer.rejection_reason}",
                type=NotificationType.REJECTION,
                document_id=document_id
            )

        elif all_signed:
            document.status = DocumentStatus.COMPLETED
            document.completed_at = datetime.now(timezone.utc)
            await self.repo.update(document)

            # Audit
            await self.audit_service.record_event(
                event_type=AuditEventType.DOCUMENT_COMPLETED,
                actor_type=AuditActorType.SYSTEM,
                document_id=document_id,
                event_data={"total_signers": len(signers)}
            )

            # Notify Owner
            await self.notification_service.send_notification(
                recipient_email=owner_email,
                subject=f"Document Completed: {document.title}",
                body=f"All signers have signed '{document.title}'. You can now download the finalized document.",
                type=NotificationType.COMPLETION,
                document_id=document_id
            )

        elif any_signed and document.status == DocumentStatus.PENDING:
            document.status = DocumentStatus.PARTIALLY_SIGNED
            await self.repo.update(document)

    async def get_document(self, document_id: uuid.UUID, user_id: uuid.UUID) -> Document:
        document = await self.repo.get_by_id(document_id)
        if not document:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

        if document.owner_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

        return document

    async def upload_file(
        self, document_id: uuid.UUID, user_id: uuid.UUID, file: UploadFile
    ) -> DocumentFile:
        document = await self.get_document(document_id, user_id)

        if document.status != DocumentStatus.DRAFT:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Files can only be uploaded to draft documents"
            )

        # 1. Validation
        if file.content_type != "application/pdf":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF files are allowed"
            )

        file.file.seek(0, 2)
        file_size = file.file.tell()
        file.file.seek(0)

        if file_size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File is empty"
            )

        if file_size > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File size exceeds limit of {settings.MAX_UPLOAD_SIZE_MB}MB"
            )

        # 2. Handle replacement
        old_file = await self.repo.get_original_file(document_id)

        # 3. Save new physical file
        stored_name = f"{uuid.uuid4()}.pdf"
        file_path = await self.storage.save_file(file, stored_name)

        # 4. Create record
        doc_file = DocumentFile(
            document_id=document_id,
            file_name=file.filename,
            stored_name=stored_name,
            file_path=file_path,
            file_size=file_size,
            mime_type=file.content_type,
            is_final=False
        )
        created_file = await self.repo.create_file(doc_file)

        # 5. Audit
        await self.audit_service.record_event(
            event_type=AuditEventType.DOCUMENT_UPLOADED,
            actor_type=AuditActorType.USER,
            user_id=user_id,
            document_id=document_id,
            event_data={"file_name": file.filename, "file_size": file_size}
        )

        # 6. Mark old file for physical deletion after commit
        if old_file:
            await self.repo.delete_file_record(old_file.id)
            created_file._old_path_to_delete = old_file.file_path

        return created_file

    async def get_document_file_path(self, document_id: uuid.UUID, user_id: uuid.UUID) -> str:
        document = await self.get_document(document_id, user_id)
        doc_file = await self.repo.get_original_file(document_id)

        if not doc_file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No file uploaded for this document"
            )

        return doc_file.file_path

    async def list_documents(self, owner_id: uuid.UUID, skip: int = 0, limit: int = 100) -> list[Document]:
        return await self.repo.list_by_owner(owner_id, skip, limit)

    async def update_document(
        self, document_id: uuid.UUID, user_id: uuid.UUID, doc_in: DocumentUpdate
    ) -> Document:
        document = await self.get_document(document_id, user_id)

        if document.status != DocumentStatus.DRAFT:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Only draft documents can be updated"
            )

        update_data = doc_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(document, field, value)

        updated_doc = await self.repo.update(document)

        await self.audit_service.record_event(
            event_type=AuditEventType.DOCUMENT_UPDATED,
            actor_type=AuditActorType.USER,
            user_id=user_id,
            document_id=updated_doc.id,
            event_data=update_data
        )
        return updated_doc

    async def delete_document(self, document_id: uuid.UUID, user_id: uuid.UUID) -> None:
        document = await self.get_document(document_id, user_id)

        if document.status != DocumentStatus.DRAFT:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Only draft documents can be deleted"
            )

        # Get associated files to delete from disk after DB delete
        from sqlalchemy import select
        files_result = await self.session.execute(
            select(DocumentFile).where(DocumentFile.document_id == document_id)
        )
        file_paths = [f.file_path for f in files_result.scalars().all()]

        await self.repo.delete(document_id)

        await self.audit_service.record_event(
            event_type=AuditEventType.DOCUMENT_DELETED,
            actor_type=AuditActorType.USER,
            user_id=user_id,
            document_id=document_id,
            event_data={"title": document.title}
        )

        # Attach paths to document object for cleanup in router
        document._paths_to_delete = file_paths
