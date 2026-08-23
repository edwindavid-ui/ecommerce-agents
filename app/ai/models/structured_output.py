from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class StructuredResponse(BaseModel):
    # Make negotiation fields optional with default fallbacks
    reasoning: Optional[str] = None
    decision: Optional[str] = None
    confidence: Optional[float] = 0.7
    counter_price: Optional[float] = None
    
    # Add support for recommendation rankings
    rankings: Optional[List[Dict[str, Any]]] = None

    class Config:
        extra = "allow"

class OfferResponse(BaseModel):
    reasoning: str = Field(..., min_length=1, max_length=1000)
    offer_price: float = Field(..., gt=0)
    negotiation_status: str = Field(..., min_length=1)
    confidence: float = Field(..., ge=0.0, le=1.0)
