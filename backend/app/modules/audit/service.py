import uuid
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.audit.models import AuditLog
from app.modules.audit.repository import AuditRepository
from app.common.enums import AuditActorType, AuditEventType

class AuditService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = AuditRepository(session)

    async def record_event(
        self,
        event_type: AuditEventType,
        actor_type: AuditActorType,
        user_id: uuid.UUID | None = None,
        document_id: uuid.UUID | None = None,
        event_data: dict[str, Any] | None = None,
    ) -> AuditLog:
        """
        Records an immutable audit event.
        """
        audit_log = AuditLog(
            event_type=event_type,
            actor_type=actor_type,
            user_id=user_id,
            document_id=document_id,
            event_data=event_data,
        )
        return await self.repo.create(audit_log)
