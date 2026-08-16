from fastapi import APIRouter, HTTPException, status, Query
from app.db.mongodb import database
from app.db.repositories.negotiations import NegotiationRepository
from app.db.repositories.seller_agents import SellerAgentRepository
from app.db.repositories.sellers import SellerRepository, InventoryRepository
from app.db.repositories.products import ProductRepository
from app.services.seller_service import InventoryService
from app.services.seller_agent_service import SellerAgentService
from app.services.negotiation_service import NegotiationService
from app.services.ai_service import AIService
from app.schemas.negotiation import NegotiationCreate, OfferCreate, NegotiationResponse

router = APIRouter(prefix="/negotiations", tags=["negotiations"])

# --- Initialize Repositories ---
negotiation_repo = NegotiationRepository(collection=database.get_collection("negotiations"))
seller_agent_repo = SellerAgentRepository(collection=database.get_collection("seller_agents"))
seller_repo = SellerRepository(collection=database.get_collection("sellers"))
product_repo = ProductRepository(collection=database.get_collection("products"))
inventory_repo = InventoryRepository(collection=database.get_collection("inventory"))

# --- Initialize Auxiliary Services ---
inventory_service = InventoryService(inventory_repo)
ai_service = AIService()

# --- Initialize Services with Full Dependency Graph ---
negotiation_service = NegotiationService(negotiation_repo=negotiation_repo)

seller_agent_service = SellerAgentService(
    agent_repo=seller_agent_repo,
    seller_repo=seller_repo,
    product_repo=product_repo,
    inventory_service=inventory_service,
    negotiation_service=negotiation_service,
    ai_service=ai_service
)

# Complete the circular reference loop
negotiation_service.seller_agent_service = seller_agent_service

@router.post("", status_code=status.HTTP_201_CREATED, response_model=NegotiationResponse)
async def create_negotiation(payload: NegotiationCreate):
    try:
        return await negotiation_service.start_negotiation(payload)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{neg_id}", status_code=status.HTTP_200_OK, response_model=NegotiationResponse)
async def get_negotiation(neg_id: str):
    try:
        return await negotiation_service.get_negotiation(neg_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/{neg_id}/offers", status_code=status.HTTP_200_OK, response_model=NegotiationResponse)
async def submit_offer(
    neg_id: str, 
    payload: OfferCreate, 
    sender: str = Query(..., description="Identify who is making the offer: 'buyer' or 'seller'")
):
    """
    Submit a counter-offer. 
    Note: In production, the 'sender' would be securely extracted from the authenticated agent token, not a query parameter.
    """
    if sender not in ["buyer", "seller"]:
        raise HTTPException(status_code=400, detail="Sender must be 'buyer' or 'seller'.")
        
    try:
        return await negotiation_service.submit_offer(neg_id, sender, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{neg_id}/accept", status_code=status.HTTP_200_OK, response_model=NegotiationResponse)
async def accept_negotiation(neg_id: str):
    try:
        return await negotiation_service.accept_offer(neg_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{neg_id}/reject", status_code=status.HTTP_200_OK, response_model=NegotiationResponse)
async def reject_negotiation(neg_id: str):
    try:
        return await negotiation_service.reject_negotiation(neg_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{neg_id}/cancel", status_code=status.HTTP_200_OK, response_model=NegotiationResponse)
async def cancel_negotiation(neg_id: str):
    try:
        return await negotiation_service.cancel_negotiation(neg_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
