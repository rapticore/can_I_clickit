from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    user_id: str
    email: str
    tier: str
    grandma_mode: bool
    api_key: str | None = None


class MeResponse(BaseModel):
    user_id: str
    email: str
    tier: str
    grandma_mode: bool
    language: str
    api_key: str | None = None


class UpdateProfileRequest(BaseModel):
    grandma_mode: bool | None = None
    language: str | None = None
