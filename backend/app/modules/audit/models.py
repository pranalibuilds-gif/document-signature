import uuid
from typing import Any
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, Enum, UUID, Index
from sqlalchemy.dialects.postgresql import JSONB
from app.common.models import UUIDMixin, TimestampMixin
from app.common.enums import AuditActorType, AuditEventType
from app.core.database import Base

class AuditLog(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "audit_logs"

    # We use UUID type for document_id without ForeignKey for now as documents table doesn't exist yet.
    # It will be linked in Phase 3.0.
    document_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)

    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    actor_type: Mapped[AuditActorType] = mapped_column(
        Enum(AuditActorType), nullable=False, index=True
    )

    event_type: Mapped[AuditEventType] = mapped_column(
        Enum(AuditEventType), nullable=False, index=True
    )

    # event_data uses JSONB for PostgreSQL optimization
    event_data: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)

    # Indices for performance (as approved)
    __table_args__ = (
        Index("ix_audit_logs_document_id_created_at", "document_id", "created_at"),
        Index("ix_audit_logs_user_id_created_at", "user_id", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<AuditLog {self.event_type} by {self.actor_type}>"
