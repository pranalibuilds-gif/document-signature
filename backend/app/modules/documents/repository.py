import uuid
from sqlalchemy import select, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.documents.models import Document, DocumentFile

class DocumentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, document: Document) -> Document:
        self.session.add(document)
        await self.session.flush()
        return document

    async def get_by_id(self, document_id: uuid.UUID) -> Document | None:
        result = await self.session.execute(
            select(Document).where(Document.id == document_id)
        )
        return result.scalar_one_or_none()

    async def list_by_owner(
        self, owner_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> list[Document]:
        result = await self.session.execute(
            select(Document)
            .where(Document.owner_id == owner_id)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def update(self, document: Document) -> Document:
        self.session.add(document)
        await self.session.flush()
        return document

    async def delete(self, document_id: uuid.UUID) -> None:
        await self.session.execute(
            delete(Document).where(Document.id == document_id)
        )

    # File operations
    async def create_file(self, document_file: DocumentFile) -> DocumentFile:
        self.session.add(document_file)
        await self.session.flush()
        return document_file

    async def get_original_file(self, document_id: uuid.UUID) -> DocumentFile | None:
        result = await self.session.execute(
            select(DocumentFile)
            .where(
                and_(
                    DocumentFile.document_id == document_id,
                    DocumentFile.is_final == False
                )
            )
            .order_by(DocumentFile.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def delete_file_record(self, file_id: uuid.UUID) -> None:
        await self.session.execute(
            delete(DocumentFile).where(DocumentFile.id == file_id)
        )
