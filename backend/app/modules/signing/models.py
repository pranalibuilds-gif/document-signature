import uuid
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, UUID, DateTime, Text
from app.common.models import UUIDMixin, TimestampMixin
from app.core.database import Base

class FieldValue(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "field_values"

    field_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("signature_fields.id", ondelete="CASCADE"), nullable=False, unique=True
    )

    document_signer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("document_signers.id", ondelete="CASCADE"), nullable=False, index=True
    )

    value: Mapped[str] = mapped_column(Text, nullable=False)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Relationships
    field = relationship("SignatureField", backref="value_record")
    signer = relationship("DocumentSigner", backref="field_values")

    def __repr__(self) -> str:
        return f"<FieldValue field_id={self.field_id} signer_id={self.document_signer_id}>"
