from typing import Optional
from pydantic import BaseModel, Field


from pydantic import BaseModel, Field
from typing import Any, Optional, List

class RecommendationRequest(BaseModel):
    query: Optional[str] = Field(default=None, description="Search keyword or user intent description")
    category: Optional[str] = Field(default=None, description="Product category filter")
    min_price: Optional[float] = Field(default=None, ge=0, description="Minimum price boundary")
    max_price: Optional[float] = Field(default=None, ge=0, description="Maximum budget boundary")
    preferences: dict[str, Any] = Field(default={}, description="Key-value product attributes (e.g., ramGB, storageGB)")
    limit: int = Field(default=10, ge=1, le=50, description="Maximum number of recommendations to return")

class RecommendationItem(BaseModel):
    product_id: str
    seller_id: str
    score: float = Field(..., ge=0, le=1, description="AI confidence or utility ranking score")
    reason: str = Field(..., description="Explanation for why this product fits the user")
    product: dict = Field(..., description="Full product metadata details")

class RecommendationResponse(BaseModel):
    request_id: str
    results: List[RecommendationItem]