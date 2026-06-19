import uuid
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.fields.models import SignatureField
from app.modules.fields.repository import SignatureFieldRepository
from app.modules.fields.schemas import SignatureFieldCreate, SignatureFieldUpdate
from app.modules.signers.repository import SignerRepository
from app.modules.audit.service import AuditService
from app.common.enums import DocumentStatus, AuditActorType, AuditEventType

class FieldService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = SignatureFieldRepository(session)
        # Avoid circular import by using local import or document repository directly
        self.signer_repo = SignerRepository(session)
        self.audit_service = AuditService(session)

    async def _get_document_checked(self, document_id: uuid.UUID, user_id: uuid.UUID):
        from app.modules.documents.repository import DocumentRepository
        doc_repo = DocumentRepository(self.session)
        document = await doc_repo.get_by_id(document_id)
        if not document:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
        if document.owner_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        return document

    async def add_field(
        self, document_id: uuid.UUID, user_id: uuid.UUID, field_in: SignatureFieldCreate
    ) -> SignatureField:
        # 1. Validate ownership and DRAFT status
        document = await self._get_document_checked(document_id, user_id)
        if document.status != DocumentStatus.DRAFT:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Fields can only be added to draft documents"
            )

        # 2. Validate signer belongs to document
        signer = await self.signer_repo.get_by_id(field_in.assigned_signer_id)
        if not signer or signer.document_id != document_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Signer does not belong to this document"
            )

        # 3. Create field
        field = SignatureField(
            document_id=document_id,
            **field_in.model_dump()
        )
        created_field = await self.repo.create(field)

        # 4. Audit
        await self.audit_service.record_event(
            event_type=AuditEventType.FIELD_CREATED,
            actor_type=AuditActorType.USER,
            user_id=user_id,
            document_id=document_id,
            event_data={
                "field_type": created_field.field_type,
                "signer_email": signer.email,
                "page": created_field.page_number,
                "pre_filled": bool(created_field.pre_filled_value)
            }
        )

        return created_field

    async def remove_field(
        self, document_id: uuid.UUID, user_id: uuid.UUID, field_id: uuid.UUID
    ) -> None:
        # 1. Validate ownership and DRAFT status
        document = await self._get_document_checked(document_id, user_id)
        if document.status != DocumentStatus.DRAFT:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Fields can only be removed from draft documents"
            )

        # 2. Check if field exists
        field = await self.repo.get_by_id(field_id)
        if not field or field.document_id != document_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Field not found in this document"
            )

        field_type = field.field_type
        page_num = field.page_number

        # 3. Get signer email for audit before delete
        signer = await self.signer_repo.get_by_id(field.assigned_signer_id)
        signer_email = signer.email if signer else "Unknown"

        # 4. Remove field
        await self.repo.delete(field_id)

        # 5. Audit
        await self.audit_service.record_event(
            event_type=AuditEventType.FIELD_REMOVED,
            actor_type=AuditActorType.USER,
            user_id=user_id,
            document_id=document_id,
            event_data={
                "field_type": field_type,
                "signer_email": signer_email,
                "page": page_num
            }
        )

    async def update_field(
        self, document_id: uuid.UUID, user_id: uuid.UUID, field_id: uuid.UUID, field_in: SignatureFieldUpdate
    ) -> SignatureField:
        # 1. Validate ownership and DRAFT status
        document = await self._get_document_checked(document_id, user_id)
        if document.status != DocumentStatus.DRAFT:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Fields can only be updated on draft documents"
            )

        # 2. Check if field exists
        field = await self.repo.get_by_id(field_id)
        if not field or field.document_id != document_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Field not found in this document"
            )

        # 3. Apply updates
        update_data = field_in.model_dump(exclude_unset=True)

        # If changing signer, validate it
        if "assigned_signer_id" in update_data:
            new_signer_id = update_data["assigned_signer_id"]
            signer = await self.signer_repo.get_by_id(new_signer_id)
            if not signer or signer.document_id != document_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="New signer does not belong to this document"
                )

        for key, value in update_data.items():
            setattr(field, key, value)

        updated_field = await self.repo.update(field)

        # 4. Audit
        await self.audit_service.record_event(
            event_type=AuditEventType.FIELD_UPDATED,
            actor_type=AuditActorType.USER,
            user_id=user_id,
            document_id=document_id,
            event_data={
                "field_id": str(field_id),
                "field_type": updated_field.field_type
            }
        )

        return updated_field

    async def list_fields(self, document_id: uuid.UUID, user_id: uuid.UUID) -> list[SignatureField]:
        # Validate ownership
        await self._get_document_checked(document_id, user_id)
        return await self.repo.list_by_document(document_id)

    async def validate_document_ready_for_signing(self, document_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """
        Validates if document is ready to be sent for signing.
        Checks: Has PDF, Has Signers, Every Signer has >= 1 field.
        """
        await self._get_document_checked(document_id, user_id)

        # 1. Check if PDF exists
        from app.modules.documents.repository import DocumentRepository
        doc_repo = DocumentRepository(self.session)
        pdf = await doc_repo.get_original_file(document_id)
        if not pdf:
            return False

        # 2. Check if signers exist
        signers = await self.signer_repo.list_by_document(document_id)
        if not signers:
            return False

        # 3. Check every signer has at least one field
        for signer in signers:
            fields = await self.repo.list_by_signer(signer.id)
            if not fields:
                return False

        return True
