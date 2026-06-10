import uuid
from datetime import datetime
from pydantic import Field
from app.common.schemas import BaseSchema, IDSchema, TimestampSchema
from app.common.enums import DocumentStatus

class DocumentBase(BaseSchema):
    title: str = Field(..., max_length=255)
    description: str | None = None
    expires_at: datetime | None = None

class DocumentCreate(DocumentBase):
    pass

class DocumentUpdate(BaseSchema):
    title: str | None = Field(None, max_length=255)
    description: str | None = None
    expires_at: datetime | None = None

class DocumentRead(DocumentBase, IDSchema, TimestampSchema):
    owner_id: uuid.UUID
    status: DocumentStatus
    completed_at: datetime | None = None
    rejected_at: datetime | None = None
