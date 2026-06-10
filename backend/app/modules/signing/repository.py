import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.signing.models import FieldValue

class SigningRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_field_value(self, field_value: FieldValue) -> FieldValue:
        self.session.add(field_value)
        await self.session.flush()
        return field_value

    async def get_field_values_by_signer(self, signer_id: uuid.UUID) -> list[FieldValue]:
        result = await self.session.execute(
            select(FieldValue).where(FieldValue.document_signer_id == signer_id)
        )
        return list(result.scalars().all())
