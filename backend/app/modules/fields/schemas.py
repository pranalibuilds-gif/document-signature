import uuid
from pydantic import Field, field_validator
from app.common.schemas import BaseSchema, IDSchema, TimestampSchema
from app.common.enums import FieldType

class SignatureFieldBase(BaseSchema):
    assigned_signer_id: uuid.UUID
    page_number: int = Field(..., ge=1)
    x_coordinate: float = Field(..., ge=0)
    y_coordinate: float = Field(..., ge=0)
    width: float = Field(..., gt=0)
    height: float = Field(..., gt=0)
    field_type: FieldType
    required: bool = True

class SignatureFieldCreate(SignatureFieldBase):
    pass

class SignatureFieldRead(SignatureFieldBase, IDSchema, TimestampSchema):
    document_id: uuid.UUID
