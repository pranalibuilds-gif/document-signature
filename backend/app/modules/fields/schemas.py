import uuid
from pydantic import Field
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

class SignatureFieldUpdate(BaseSchema):
    assigned_signer_id: uuid.UUID | None = None
    page_number: int | None = Field(None, ge=1)
    x_coordinate: float | None = Field(None, ge=0)
    y_coordinate: float | None = Field(None, ge=0)
    width: float | None = Field(None, gt=0)
    height: float | None = Field(None, gt=0)
    field_type: FieldType | None = None
    required: bool | None = None

class SignatureFieldRead(SignatureFieldBase, IDSchema, TimestampSchema):
    document_id: uuid.UUID
