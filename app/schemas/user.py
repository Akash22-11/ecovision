"""Pydantic schemas for user registration, login, and profile responses."""

from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from app.utils.constants import UserRole


class UserRegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=120, examples=["Asha Rao"])
    email: EmailStr = Field(..., examples=["asha@example.com"])
    password: str = Field(..., min_length=8, max_length=128, examples=["StrongPass123"])
    role: UserRole = Field(default=UserRole.CITIZEN, description="citizen or municipality_admin")


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    role: UserRole
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
