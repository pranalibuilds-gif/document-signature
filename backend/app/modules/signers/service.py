import uuid
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.signers.models import DocumentSigner
from app.modules.signers.repository import SignerRepository
from app.modules.signers.schemas import SignerCreate
from app.modules.documents.service import DocumentService
from app.modules.users.repository import UserRepository
from app.modules.audit.service import AuditService
from app.common.enums import DocumentStatus, SignerStatus, AuditActorType, AuditEventType
from app.core.config import settings

class SignerService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = SignerRepository(session)
        self.doc_service = DocumentService(session)
        self.user_repo = UserRepository(session)
        self.audit_service = AuditService(session)

    async def add_signer(
        self, document_id: uuid.UUID, user_id: uuid.UUID, signer_in: SignerCreate
    ) -> DocumentSigner:
        # 1. Validate document ownership and DRAFT status
        document = await self.doc_service.get_document(document_id, user_id)
        if document.status != DocumentStatus.DRAFT:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Signers can only be added to draft documents"
            )

        # 2. Check signer limit
        current_count = await self.repo.count_by_document(document_id)
        if current_count >= settings.MAX_SIGNERS_PER_DOCUMENT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Maximum of {settings.MAX_SIGNERS_PER_DOCUMENT} signers allowed per document"
            )

        # 3. Check for duplicate email
        existing = await self.repo.get_by_email(document_id, signer_in.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This email is already a signer for this document"
            )

        # 4. Lookup existing user to link user_id
        linked_user = await self.user_repo.get_by_email(signer_in.email)
        linked_user_id = linked_user.id if linked_user else None

        # 5. Create signer
        signer = DocumentSigner(
            document_id=document_id,
            email=signer_in.email,
            user_id=linked_user_id,
            status=SignerStatus.PENDING
        )
        created_signer = await self.repo.add(signer)

        # 6. Audit event
        await self.audit_service.record_event(
            event_type=AuditEventType.SIGNER_ADDED,
            actor_type=AuditActorType.USER,
            user_id=user_id,
            document_id=document_id,
            event_data={"email": created_signer.email}
        )

        return created_signer

    async def remove_signer(
        self, document_id: uuid.UUID, user_id: uuid.UUID, signer_id: uuid.UUID
    ) -> None:
        # 1. Validate document ownership and DRAFT status
        document = await self.doc_service.get_document(document_id, user_id)
        if document.status != DocumentStatus.DRAFT:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Signers can only be removed from draft documents"
            )

        # 2. Check if signer exists
        signer = await self.repo.get_by_id(signer_id)
        if not signer or signer.document_id != document_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Signer not found in this document"
            )

        signer_email = signer.email

        # 3. Remove signer
        await self.repo.remove(signer_id)

        # 4. Audit event
        await self.audit_service.record_event(
            event_type=AuditEventType.SIGNER_REMOVED,
            actor_type=AuditActorType.USER,
            user_id=user_id,
            document_id=document_id,
            event_data={"email": signer_email}
        )

    async def list_signers(self, document_id: uuid.UUID, user_id: uuid.UUID) -> list[DocumentSigner]:
        # Validate ownership
        await self.doc_service.get_document(document_id, user_id)
        return await self.repo.list_by_document(document_id)
