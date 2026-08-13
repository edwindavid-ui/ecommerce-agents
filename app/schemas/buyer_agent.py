from typing import Optional

from pydantic import BaseModel, Field


class BuyerTaskCreate(BaseModel):
    buyer_id: str = Field(..., min_length=1)
    requirement: str = Field(..., min_length=10, max_length=1000)
    budget: float = Field(..., gt=0)
    category: Optional[str] = None
    min_price: Optional[float] = None


class BuyerTaskResponse(BaseModel):
    task_id: str
    buyer_id: str
    requirement: str
    budget: float
    category: Optional[str]
    status: str
    selected_seller_id: Optional[str] = None
    selected_product_id: Optional[str] = None
    recommendation_id: Optional[str] = None
    created_at: str
    updated_at: str


class BuyerAgentState(BaseModel):
    task_id: str
    state: str  # IDLE, TASK_CREATED, ANALYZING_REQUIREMENTS, SEARCHING, EVALUATING_PRODUCTS, SELECTING_SELLER, NEGOTIATING, AGREEMENT, COMPLETED
    analysis_result: Optional[dict] = None
    product_candidates: Optional[list[dict]] = None
    selected_product_id: Optional[str] = None
    selected_seller_id: Optional[str] = None
    history: list[dict] = Field(default_factory=list)
