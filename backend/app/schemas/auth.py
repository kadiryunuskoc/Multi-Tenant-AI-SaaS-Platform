from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class TenantBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)


class TenantCreate(TenantBase):
    pass


class TenantResponse(TenantBase):
    id: int
    api_key: str
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    role: str = Field(default="user", pattern="^(admin|user|viewer)$")


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    tenant_id: int


class UserResponse(UserBase):
    id: int
    tenant_id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class RefreshTokenRequest(BaseModel):
    refresh_token: str
