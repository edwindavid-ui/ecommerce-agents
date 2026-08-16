from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime

class OrderCreate(BaseModel):
    negotiation_id: str = Field(..., min_length=1, description="ID of the successfully accepted negotiation")

class OrderStatusUpdate(BaseModel):
    status: Literal["confirmed", "processing", "completed", "cancelled"]

class OrderResponse(BaseModel):
    id: str
    order_number: str
    buyer_id: str
    seller_id: str
    product_id: str
    negotiation_id: str
    quantity: int
    unit_price: float
    total_price: float
    currency: str = "NGN"
    status: str
    created_at: str
    updated_at: str

    class Config:
        populate_by_name = True