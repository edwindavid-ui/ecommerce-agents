from pydantic import BaseModel, Field


class StructuredResponse(BaseModel):
    reasoning: str = Field(..., min_length=1, max_length=1000)
    decision: str = Field(..., min_length=1, max_length=100)
    confidence: float = Field(..., ge=0.0, le=1.0)


class ToolCall(BaseModel):
    tool_name: str = Field(..., min_length=1)
    parameters: dict = Field(default_factory=dict)
    purpose: str = Field(..., min_length=1, max_length=500)


class OfferResponse(BaseModel):
    reasoning: str = Field(..., min_length=1, max_length=1000)
    offer_price: float = Field(..., gt=0)
    negotiation_status: str = Field(..., min_length=1)
    confidence: float = Field(..., ge=0.0, le=1.0)
