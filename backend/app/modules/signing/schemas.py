import uuid
from typing import List
from datetime import datetime
from pydantic import BaseModel, Field
from app.common.schemas import BaseSchema, IDSchema, TimestampSchema
from app.modules.documents.schemas import DocumentRead
from app.modules.signers.schemas import SignerRead
from app.modules.fields.schemas import SignatureFieldRead

class FieldValueCreate(BaseModel):
    field_id: uuid.UUID
    value: str

class SigningSubmission(BaseModel):
    values: List[FieldValueCreate]

class SigningSessionRead(BaseModel):
    document: DocumentRead
    signer: SignerRead
    fields: List[SignatureFieldRead]

class RejectionRequest(BaseModel):
    reason: str = Field(..., min_length=1, max_length=500)
