from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class NegotiationCreate(BaseModel):
    buyer_id: str = Field(..., min_length=1)
    seller_id: str = Field(..., min_length=1)
    product_id: str = Field(..., min_length=1)
    
    initial_offer: float = Field(..., gt=0)
    max_price: float = Field(..., gt=0, description="Buyer's hard ceiling limit")
    
    currency: str = "NGN"
    max_rounds: int = Field(default=5, ge=1, le=20)

class OfferCreate(BaseModel):
    price: float = Field(..., gt=0)
    message: Optional[str] = None

class OfferResponse(BaseModel):
    round: int
    party: str
    price: float
    message: Optional[str]
    created_at: str

class NegotiationResponse(BaseModel):
    id: str
    buyer_id: str
    seller_id: str
    product_id: str
    
    initial_price: float
    current_offer: float
    final_price: Optional[float] = None
    
    currency: str
    round: int
    max_rounds: int
    
    status: str
    current_turn: str
    offers: List[OfferResponse] = []