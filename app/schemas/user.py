from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    email: EmailStr
    role: str = "buyer"

    @field_validator("role")
    @classmethod
    def validate_role(cls, value: str) -> str:
        allowed_roles = {"buyer", "seller", "admin"}
        if value not in allowed_roles:
            raise ValueError(f"role must be one of {sorted(allowed_roles)}")
        return value


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)


class UserResponse(UserBase):
    id: str


class UserUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    email: Optional[EmailStr] = None
    role: Optional[str] = None

    @field_validator("role")
    @classmethod
    def validate_role(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        allowed_roles = {"buyer", "seller", "admin"}
        if value not in allowed_roles:
            raise ValueError(f"role must be one of {sorted(allowed_roles)}")
        return value
