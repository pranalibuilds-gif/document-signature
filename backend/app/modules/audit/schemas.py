from typing import Any
import uuid
from pydantic import Field
from app.common.schemas import BaseSchema, IDSchema, TimestampSchema
from app.common.enums import AuditActorType, AuditEventType

class AuditLogRead(IDSchema, TimestampSchema):
    document_id: uuid.UUID | None
    user_id: uuid.UUID | None
    actor_type: AuditActorType
    event_type: AuditEventType
    event_data: dict[str, Any] | None
