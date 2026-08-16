from typing import Optional, Any
from pydantic import BaseModel, Field, field_validator


class ProductBase(BaseModel):
    seller_id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=2)
    description: str = Field(..., min_length=1)
    category: str = Field(..., min_length=1)
    price: float = Field(..., gt=0)
    currency: str = "NGN"
    attributes: dict[str, Any] = {}
    # active: bool = True
    status: str = "active"  # <-- Define the field here

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
    name: Optional[str] = Field(default=None, min_length=2)
    description: Optional[str] = Field(default=None, min_length=1)
    category: Optional[str] = Field(default=None, min_length=1)
    price: Optional[float] = Field(default=None, gt=0)
    currency: Optional[str] = None
    attributes: dict[str, Any] = {}
    # active: Optional[bool] = None
    status: str = "active"  # <-- Define the field here

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str | None) -> str | None:
        if value is None:
            return value
        allowed = {"active", "draft", "archived"}
        if value not in allowed:
            raise ValueError(f"status must be one of {sorted(allowed)}")
        return value
