from typing import Optional
from pydantic import BaseModel, Field, EmailStr
class SellerBase(BaseModel):
    business_name: str = Field(..., min_length=2, description="Name of the seller's business")
    description: Optional[str] = Field(default=None, description="Short bio or overview of the shop")
    contact_email: EmailStr = Field(..., description="Business contact email")
    phone: Optional[str] = Field(default=None, description="Contact phone number")
    status: str = Field(default="active", description="Account status (active/suspended)")

class SellerCreate(SellerBase):
    pass

class SellerUpdate(BaseModel):
    business_name: Optional[str] = Field(default=None, min_length=2)
    description: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    phone: Optional[str] = None
    status: Optional[str] = None

class SellerNegotiationConfig(BaseModel):
    negotiation_enabled: bool = Field(default=True, description="Flag indicating if the seller agent can negotiate")
    min_discount_percent: float = Field(..., ge=0, le=100, description="Minimum discount threshold the agent can offer")
    max_discount_percent: float = Field(..., ge=0, le=100, description="Maximum discount ceiling the agent can offer")

class SellerResponse(SellerBase):
    id: str
    user_id: str
    negotiation_config: Optional[SellerNegotiationConfig] = None

class InventoryBase(BaseModel):
    product_id: str = Field(..., min_length=1)
    seller_id: str = Field(..., min_length=1)
    quantity: int = Field(..., ge=0)

class InventoryCreate(InventoryBase):
    pass

class InventoryUpdate(BaseModel):
    quantity: int = Field(..., ge=0, description="Updated total physical quantity")

class InventoryReservation(BaseModel):
    quantity: int = Field(..., gt=0, description="Quantity to reserve during negotiation")

class InventoryRelease(BaseModel):
    quantity: int = Field(..., gt=0, description="Quantity to release if negotiation fails")

class InventoryResponse(InventoryBase):
    id: str
    available_quantity: int
    reserved_quantity: int