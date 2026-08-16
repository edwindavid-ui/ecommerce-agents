from typing import Optional, Dict, Any, List
from pydantic import BaseModel, EmailStr, Field, field_validator


class UserBase(BaseModel):
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    role: str = "buyer"

    @field_validator("role")
    @classmethod
    def validate_role(cls, value: str) -> str:
        allowed_roles = {"buyer", "seller", "admin"}
        if value not in allowed_roles:
            raise ValueError(f"role must be one of {sorted(allowed_roles)}")
        return value


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=72)


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=72)


class UserPreferences(BaseModel):
    currency: str = "NGN"
    preferred_categories: List[str] = []
    preferred_brands: List[str] = []
    default_max_budget: Optional[float] = Field(default=None, ge=0)


class UserResponse(UserBase):
    id: str
    status: str = "active"
    preferences: Optional[Dict[str, Any]] = {}
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class UserUpdate(BaseModel):
    first_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
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