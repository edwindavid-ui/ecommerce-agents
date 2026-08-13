from typing import Optional

from pydantic import BaseModel, Field, field_validator


class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    category: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    seller_id: str = Field(..., min_length=1)
    status: str = Field(default="active")

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str) -> str:
        allowed = {"active", "draft", "archived"}
        if value not in allowed:
            raise ValueError(f"status must be one of {sorted(allowed)}")
        return value


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    category: Optional[str] = Field(default=None, min_length=1, max_length=100)
    description: Optional[str] = None
    price: Optional[float] = Field(default=None, gt=0)
    status: Optional[str] = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str | None) -> str | None:
        if value is None:
            return value
        allowed = {"active", "draft", "archived"}
        if value not in allowed:
            raise ValueError(f"status must be one of {sorted(allowed)}")
        return value
