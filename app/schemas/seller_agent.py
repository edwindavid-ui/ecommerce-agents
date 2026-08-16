from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class SellerAgentCreate(BaseModel):
    seller_id: str = Field(..., min_length=1, description="Associated seller ID")
    name: str = Field(..., min_length=2, description="Agent display name")
    list_price: Optional[float] = Field(default=None, gt=0)
    min_price: Optional[float] = Field(default=None, gt=0)
    target_price: Optional[float] = Field(default=None, gt=0)
    max_negotiation_rounds: int = Field(default=5, ge=1, le=20)


class SellerAgentRespondRequest(BaseModel):
    negotiation_id: str = Field(..., min_length=1, description="The active negotiation room ID to respond to")


class OfferEvaluationRequest(BaseModel):
    offer_price: float = Field(..., gt=0, description="The incoming buyer offer price to evaluate")


class OfferEvaluationResult(BaseModel):
    decision: str = Field(..., description="Decision outcome: accept, counter, or reject")
    reasoning: Optional[str] = None
    counter_price: Optional[float] = None
    confidence: float = 1.0


class SellerAgentResponse(BaseModel):
    id: str
    seller_id: str
    name: str
    status: str = Field(..., description="State: created, idle, processing, negotiating, completed, paused, failed, deactivated")
    active_negotiations: int = 0
    current_round: int = 1
    events: List[Dict[str, Any]] = []

    class Config:
        populate_by_name = True