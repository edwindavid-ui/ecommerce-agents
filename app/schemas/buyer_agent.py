from pydantic import BaseModel, Field
from typing import Any, Optional, List

class BuyerAgentCreate(BaseModel):
    objective: str = Field(..., min_length=3, description="What the buyer wants to achieve")
    category: Optional[str] = Field(default=None, description="Target product category")
    min_budget: Optional[float] = Field(default=None, ge=0, description="Minimum acceptable budget boundary")
    max_budget: Optional[float] = Field(default=None, ge=0, description="Maximum budget boundary")
    preferences: dict[str, Any] = Field(default={}, description="Key-value product attributes like RAM or CPU")

class BuyerAgentResponse(BaseModel):
    id: str
    user_id: str
    objective: str
    status: str = Field(..., description="Current state: created, searching, evaluating, negotiating, accepted, completed, failed")
    category: Optional[str] = None
    min_budget: Optional[float] = None
    max_budget: Optional[float] = None
    preferences: dict[str, Any] = {}
    current_product_id: Optional[str] = None
    current_seller_id: Optional[str] = None
    events: List[dict] = []

# Aliases to match service imports
BuyerTaskCreate = BuyerAgentCreate
BuyerAgentState = BuyerAgentResponse