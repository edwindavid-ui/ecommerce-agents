from typing import Optional

from pydantic import BaseModel, Field


class OrderCreate(BaseModel):
    negotiation_id: str = Field(..., min_length=1)


class OrderResponse(BaseModel):
    order_id: str
    negotiation_id: str
    buyer_id: str
    seller_id: str
    product_id: str
    final_price: float
    status: str  # pending, confirmed, processing, delivered, cancelled
    created_at: str
    updated_at: str


class OrderStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(pending|confirmed|processing|delivered|cancelled)$")
