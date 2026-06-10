import uuid
from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.signers.models import DocumentSigner, SigningToken

class SignerRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, signer: DocumentSigner) -> DocumentSigner:
        self.session.add(signer)
        await self.session.flush()
        return signer

    async def remove(self, signer_id: uuid.UUID) -> None:
        await self.session.execute(
            delete(DocumentSigner).where(DocumentSigner.id == signer_id)
        )

    async def get_by_id(self, signer_id: uuid.UUID) -> DocumentSigner | None:
        result = await self.session.execute(
            select(DocumentSigner).where(DocumentSigner.id == signer_id)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, document_id: uuid.UUID, email: str) -> DocumentSigner | None:
        result = await self.session.execute(
            select(DocumentSigner)
            .where(DocumentSigner.document_id == document_id)
            .where(DocumentSigner.email == email)
        )
        return result.scalar_one_or_none()

    async def list_by_document(self, document_id: uuid.UUID) -> list[DocumentSigner]:
        result = await self.session.execute(
            select(DocumentSigner).where(DocumentSigner.document_id == document_id)
        )
        return list(result.scalars().all())

    async def count_by_document(self, document_id: uuid.UUID) -> int:
        result = await self.session.execute(
            select(func.count()).select_from(DocumentSigner).where(DocumentSigner.document_id == document_id)
        )
        return result.scalar_one()

    # Token operations
    async def create_token(self, token: SigningToken) -> SigningToken:
        self.session.add(token)
        await self.session.flush()
        return token

    async def get_token_by_hash(self, token_hash: str) -> SigningToken | None:
        result = await self.session.execute(
            select(SigningToken).where(SigningToken.token_hash == token_hash)
        )
        return result.scalar_one_or_none()
