import uuid
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.documents.models import Document
from app.modules.documents.repository import DocumentRepository
from app.modules.documents.schemas import DocumentCreate, DocumentUpdate
from app.modules.audit.service import AuditService
from app.common.enums import DocumentStatus, AuditActorType, AuditEventType

class DocumentService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = DocumentRepository(session)
        self.audit_service = AuditService(session)

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

    async def get_document(self, document_id: uuid.UUID, user_id: uuid.UUID) -> Document:
        document = await self.repo.get_by_id(document_id)
        if not document:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

        if document.owner_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

        return document

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

        await self.repo.delete(document_id)

        await self.audit_service.record_event(
            event_type=AuditEventType.DOCUMENT_DELETED,
            actor_type=AuditActorType.USER,
            user_id=user_id,
            document_id=document_id,
            event_data={"title": document.title}
        )
