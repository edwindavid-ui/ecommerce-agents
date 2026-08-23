from pydantic import BaseModel, Field


class StructuredResponse(BaseModel):
    reasoning: str = Field(..., min_length=1, max_length=1000)
    decision: str = Field(..., min_length=1, max_length=100)
    confidence: float = Field(..., ge=0.0, le=1.0)
    counter_price: Optional[float] = None   

class OfferResponse(BaseModel):
    reasoning: str = Field(..., min_length=1, max_length=1000)
    offer_price: float = Field(..., gt=0)
    negotiation_status: str = Field(..., min_length=1)
    confidence: float = Field(..., ge=0.0, le=1.0)
