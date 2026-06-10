from pydantic import BaseModel, EmailStr
from app.common.schemas import BaseSchema

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseSchema):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshRequest(BaseModel):
    refresh_token: str

class VerifyEmailRequest(BaseModel):
    token: str
