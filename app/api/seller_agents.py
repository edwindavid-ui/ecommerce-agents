from fastapi import APIRouter, HTTPException, status, Depends
from app.db.mongodb import database
from app.auth.deps import get_current_user_id

from app.db.repositories.seller_agents import SellerAgentRepository
from app.db.repositories.sellers import SellerRepository, InventoryRepository
from app.db.repositories.products import ProductRepository
from app.db.repositories.negotiations import NegotiationRepository

from app.schemas.seller_agent import SellerAgentCreate, SellerAgentRespondRequest
from app.services.seller_agent_service import SellerAgentService
from app.services.seller_service import InventoryService
from app.services.negotiation_service import NegotiationService
from app.services.ai_service import AIService

router = APIRouter(prefix="/seller-agents", tags=["seller-agents"])

# --- Initialize Repositories ---
agent_repo = SellerAgentRepository(collection=database.get_collection("seller_agents"))
seller_repo = SellerRepository(collection=database.get_collection("sellers"))
product_repo = ProductRepository(collection=database.get_collection("products"))
inventory_repo = InventoryRepository(collection=database.get_collection("inventory"))
negotiation_repo = NegotiationRepository(collection=database.get_collection("negotiations"))

# --- Initialize Auxiliary Services ---
inventory_service = InventoryService(inventory_repo)
negotiation_service = NegotiationService(negotiation_repo)
ai_service = AIService()

# --- Initialize Core SellerAgentService with Full Dependency Graph ---
seller_agent_service = SellerAgentService(
    agent_repo=agent_repo,
    seller_repo=seller_repo,
    product_repo=product_repo,
    inventory_service=inventory_service,
    negotiation_service=negotiation_service,
    ai_service=ai_service
)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_seller_agent(
    payload: SellerAgentCreate, 
    current_user_id: str = Depends(get_current_user_id)
):
    """Create a new seller agent linked to an authenticated seller profile."""
    try:
        # Verify that the seller profile belongs to the currently authenticated user
        seller = await seller_repo.get_seller_by_id(payload.seller_id)
        if not seller or seller.get("user_id") != current_user_id:
            raise HTTPException(status_code=403, detail="Unauthorized: Seller profile does not belong to user")

        result = await seller_agent_service.create_agent(payload.seller_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except HTTPException as exc:
        raise exc
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return {"message": "Seller agent created successfully", "agent": result}

@router.get("/seller/me", status_code=status.HTTP_200_OK)
async def list_my_seller_agents(current_user_id: str = Depends(get_current_user_id)):
    """Retrieve all seller agents created by the authenticated seller."""
    # 1. Fetch the seller profile for the authenticated user
    seller = await seller_repo.get_seller_by_user_id(current_user_id)
    if not seller:
        raise HTTPException(status_code=404, detail="Seller profile not found")

    # 2. Fetch all agents linked to this seller_id using the updated repository method
    agents = await agent_repo.get_agents_by_seller_id(seller["id"])
    
    return agents

@router.get("/{agent_id}", status_code=status.HTTP_200_OK)
async def get_seller_agent(agent_id: str):
    """Retrieve a seller agent state and profile details by ID."""
    try:
        result = await seller_agent_service.get_agent(agent_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return {"agent": result}


@router.post("/{agent_id}/respond", status_code=status.HTTP_200_OK)
async def respond_to_negotiation(agent_id: str, payload: SellerAgentRespondRequest):
    """
    Trigger the seller agent to evaluate an active negotiation offer, check inventory,
    enforce policy constraints, and respond (Accept, Counter, or Reject) via the negotiation protocol.
    """
    try:
        result = await seller_agent_service.respond_to_negotiation(agent_id, payload.negotiation_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc
    return result


@router.get("/{agent_id}/history", status_code=status.HTTP_200_OK)
async def get_seller_agent_history(agent_id: str):
    """View the audit trail of decisions, policy checks, and events recorded by the seller agent."""
    try:
        agent = await seller_agent_service.get_agent(agent_id)
        return {"agent_id": agent_id, "events": agent.get("events", [])}
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
