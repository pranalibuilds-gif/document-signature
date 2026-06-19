import uuid
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.fields.models import SignatureField

class SignatureFieldRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, field: SignatureField) -> SignatureField:
        self.session.add(field)
        await self.session.flush()
        return field

    async def update(self, field: SignatureField) -> SignatureField:
        await self.session.flush()
        return field

    async def delete(self, field_id: uuid.UUID) -> None:
        await self.session.execute(
            delete(SignatureField).where(SignatureField.id == field_id)
        )

    async def get_by_id(self, field_id: uuid.UUID) -> SignatureField | None:
        result = await self.session.execute(
            select(SignatureField).where(SignatureField.id == field_id)
        )
        return result.scalar_one_or_none()

    async def list_by_document(self, document_id: uuid.UUID) -> list[SignatureField]:
        result = await self.session.execute(
            select(SignatureField).where(SignatureField.document_id == document_id)
        )
        return list(result.scalars().all())

    async def list_by_signer(self, signer_id: uuid.UUID) -> list[SignatureField]:
        result = await self.session.execute(
            select(SignatureField).where(SignatureField.assigned_signer_id == signer_id)
        )
        return list(result.scalars().all())
