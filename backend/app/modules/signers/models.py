import uuid
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Enum, UUID, DateTime, UniqueConstraint
from app.common.models import UUIDMixin, TimestampMixin
from app.common.enums import SignerStatus
from app.core.database import Base

class DocumentSigner(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "document_signers"

    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True
    )

    email: Mapped[str] = mapped_column(String(255), nullable=False)

    # user_id is NULL for non-registered users (Email-first strategy)
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )

    status: Mapped[SignerStatus] = mapped_column(
        Enum(SignerStatus), default=SignerStatus.PENDING, nullable=False, index=True
    )

    invited_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    signed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    rejected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    rejection_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Relationships
    document = relationship("Document", backref="signers")
    user = relationship("User", backref="signer_assignments")

    # Constraints
    __table_args__ = (
        UniqueConstraint("document_id", "email", name="uq_document_signer_email"),
    )

    def __repr__(self) -> str:
        return f"<DocumentSigner {self.email} for document {self.document_id}>"
