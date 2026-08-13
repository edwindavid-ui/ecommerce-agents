from typing import Optional

from pydantic import BaseModel, Field


class SellerAgentCreate(BaseModel):
    seller_id: str = Field(..., min_length=1)
    product_id: str = Field(..., min_length=1)
    list_price: float = Field(..., gt=0)
    min_price: float = Field(..., gt=0)
    target_price: float = Field(..., gt=0)
    max_negotiation_rounds: int = Field(default=5, ge=1)


class SellerAgentResponse(BaseModel):
    agent_id: str
    seller_id: str
    product_id: str
    list_price: float
    min_price: float
    target_price: float
    max_negotiation_rounds: int
    current_round: int = 0
    status: str = "active"


class OfferEvaluationRequest(BaseModel):
    offer_price: float = Field(..., gt=0)


class OfferEvaluationResult(BaseModel):
    decision: str  # accept, counter, reject
    reasoning: str
    counter_price: Optional[float] = None
    confidence: float = Field(..., ge=0.0, le=1.0)
