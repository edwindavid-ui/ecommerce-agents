from typing import Optional

from pydantic import BaseModel, Field


class NegotiationCreate(BaseModel):
    buyer_id: str = Field(..., min_length=1)
    seller_id: str = Field(..., min_length=1)
    product_id: str = Field(..., min_length=1)
    buyer_max_price: float = Field(..., gt=0)
    seller_min_price: float = Field(..., gt=0)
    seller_target_price: float = Field(..., gt=0)
    max_rounds: int = Field(default=5, ge=1)


class NegotiationResponse(BaseModel):
    negotiation_id: str
    buyer_id: str
    seller_id: str
    product_id: str
    buyer_max_price: float
    seller_min_price: float
    seller_target_price: float
    status: str
    current_round: int = 0
    current_offer: Optional[float] = None
    final_price: Optional[float] = None
    created_at: str
    updated_at: str


class OfferRequest(BaseModel):
    actor: str = Field(..., pattern="^(buyer|seller)$")
    offer_price: float = Field(..., gt=0)


class NegotiationMessage(BaseModel):
    message_id: str
    negotiation_id: str
    actor: str
    message_type: str  # offer, counter, accept, reject
    offer_price: Optional[float] = None
    reasoning: str
    created_at: str
