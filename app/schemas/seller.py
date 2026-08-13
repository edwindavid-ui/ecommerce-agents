from typing import Optional

from pydantic import BaseModel, Field


class SellerBase(BaseModel):
    business_name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None


class SellerCreate(SellerBase):
    pass


class SellerResponse(SellerBase):
    id: str
    user_id: str
    rating: float = 0.0
    status: str = "active"


class InventoryBase(BaseModel):
    product_id: str = Field(..., min_length=1)
    quantity: int = Field(..., ge=0)


class InventoryCreate(InventoryBase):
    pass


class InventoryUpdate(BaseModel):
    quantity: int = Field(..., ge=0)


class InventoryResponse(InventoryBase):
    id: str
    available_quantity: int
    reserved_quantity: int
