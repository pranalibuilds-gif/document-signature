from pydantic import EmailStr, Field
from app.common.schemas import BaseSchema, IDSchema, TimestampSchema
from app.common.enums import UserRole

class UserBase(BaseSchema):
    email: EmailStr
    first_name: str | None = Field(None, max_length=100)
    last_name: str | None = Field(None, max_length=100)

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    role: UserRole = UserRole.USER

class UserUpdate(BaseSchema):
    email: EmailStr | None = None
    first_name: str | None = Field(None, max_length=100)
    last_name: str | None = Field(None, max_length=100)
    password: str | None = Field(None, min_length=8)
    role: UserRole | None = None

class UserRead(UserBase, IDSchema, TimestampSchema):
    is_active: bool
    is_verified: bool
    role: UserRole
