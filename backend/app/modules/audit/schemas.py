from typing import Any
import uuid
from app.common.schemas import IDSchema, TimestampSchema
from app.common.enums import AuditActorType, AuditEventType

class AuditLogRead(IDSchema, TimestampSchema):
    document_id: uuid.UUID | None
    user_id: uuid.UUID | None
    actor_type: AuditActorType
    event_type: AuditEventType
    event_data: dict[str, Any] | None
