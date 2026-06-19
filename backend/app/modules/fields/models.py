import uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Enum, UUID, Integer, Float, Boolean, String
from app.common.models import UUIDMixin, TimestampMixin
from app.common.enums import FieldType
from app.core.database import Base

class SignatureField(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "signature_fields"

    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True
    )

    assigned_signer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("document_signers.id", ondelete="CASCADE"), nullable=False, index=True
    )

    page_number: Mapped[int] = mapped_column(Integer, nullable=False)

    x_coordinate: Mapped[float] = mapped_column(Float, nullable=False)
    y_coordinate: Mapped[float] = mapped_column(Float, nullable=False)

    width: Mapped[float] = mapped_column(Float, nullable=False)
    height: Mapped[float] = mapped_column(Float, nullable=False)

    field_type: Mapped[FieldType] = mapped_column(Enum(FieldType), nullable=False, index=True)

    required: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    pre_filled_value: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Relationships
    document = relationship("Document", backref="fields")
    signer = relationship("DocumentSigner", backref="assigned_fields")

    def __repr__(self) -> str:
        return f"<SignatureField {self.field_type} on page {self.page_number} for signer {self.assigned_signer_id}>"
