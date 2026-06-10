import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.audit.models import AuditLog

class AuditRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, audit_log: AuditLog) -> AuditLog:
        self.session.add(audit_log)
        await self.session.flush()
        return audit_log

    async def list_by_document(
        self, document_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> list[AuditLog]:
        result = await self.session.execute(
            select(AuditLog)
            .where(AuditLog.document_id == document_id)
            .order_by(AuditLog.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def list_by_user(
        self, user_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> list[AuditLog]:
        result = await self.session.execute(
            select(AuditLog)
            .where(AuditLog.user_id == user_id)
            .order_by(AuditLog.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
