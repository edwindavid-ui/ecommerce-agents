from typing import Optional

from pydantic import BaseModel, Field


class RecommendationRequest(BaseModel):
    buyer_id: str = Field(..., min_length=1)
    category: Optional[str] = None
    max_price: Optional[float] = None
    min_price: Optional[float] = None


class RecommendationResult(BaseModel):
    product_id: str
    name: str
    category: str
    price: float
    seller_id: str
    score: float


class RecommendationResponse(BaseModel):
    recommendation_id: str
    buyer_id: str
    status: str
    results: list[RecommendationResult] = []
    filters_applied: dict = {}
