import uuid
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Enum, UUID, Text, DateTime, Boolean, Integer
from app.common.models import UUIDMixin, TimestampMixin
from app.common.enums import DocumentStatus
from app.core.database import Base

class Document(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "documents"

    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    status: Mapped[DocumentStatus] = mapped_column(
        Enum(DocumentStatus), default=DocumentStatus.DRAFT, nullable=False, index=True
    )

    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    rejected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    owner = relationship("User", backref="owned_documents")
    files = relationship("DocumentFile", back_populates="document", cascade="all, delete-orphan")
    signers = relationship("DocumentSigner", back_populates="document", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Document {self.title} ({self.status})>"

class DocumentFile(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "document_files"

    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True
    )

    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    stored_name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    file_path: Mapped[str] = mapped_column(String(512), nullable=False)

    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)

    is_final: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    document = relationship("Document", back_populates="files")

    def __repr__(self) -> str:
        return f"<DocumentFile {self.file_name} (final={self.is_final})>"
