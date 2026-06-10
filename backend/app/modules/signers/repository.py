import uuid
from sqlalchemy import select, delete, func, and_, or_
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

    async def get_pending_reminders(self, days: int) -> list[DocumentSigner]:
        from datetime import datetime, timezone, timedelta
        from app.common.enums import SignerStatus, DocumentStatus
        from app.modules.documents.models import Document

        now = datetime.now(timezone.utc)
        threshold = now - timedelta(days=days)

        # Logic: Signer is PENDING, Document is active,
        # (invited_at < threshold AND last_reminder_sent_at is NULL)
        # OR (last_reminder_sent_at < threshold)

        stmt = (
            select(DocumentSigner)
            .join(Document)
            .where(DocumentSigner.status == SignerStatus.PENDING)
            .where(Document.status.in_([DocumentStatus.PENDING, DocumentStatus.PARTIALLY_SIGNED]))
            .where(
                and_(
                    DocumentSigner.invited_at < threshold,
                    or_(
                        DocumentSigner.last_reminder_sent_at.is_(None),
                        DocumentSigner.last_reminder_sent_at < threshold
                    )
                )
            )
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def cleanup_expired_signing_tokens(self, retention_days: int = 90) -> int:
        from datetime import datetime, timezone, timedelta
        now = datetime.now(timezone.utc)
        retention_threshold = now - timedelta(days=retention_days)

        # Delete tokens that are:
        # 1. Expired AND never used (expired long ago)
        # 2. Used long ago

        stmt = delete(SigningToken).where(
            or_(
                and_(SigningToken.expires_at < now, SigningToken.used_at.is_(None), SigningToken.created_at < retention_threshold),
                and_(SigningToken.used_at.is_not(None), SigningToken.used_at < retention_threshold)
            )
        )
        result = await self.session.execute(stmt)
        return result.rowcount
