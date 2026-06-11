import uuid
from datetime import datetime
from pydantic import EmailStr
from app.common.schemas import BaseSchema, IDSchema, TimestampSchema
from app.common.enums import SignerStatus

class SignerBase(BaseSchema):
    email: EmailStr

class SignerCreate(SignerBase):
    pass

class SignerRead(SignerBase, IDSchema, TimestampSchema):
    document_id: uuid.UUID
    user_id: uuid.UUID | None
    status: SignerStatus
    invited_at: datetime | None = None
    signed_at: datetime | None = None
    rejected_at: datetime | None = None
    rejection_reason: str | None = None
