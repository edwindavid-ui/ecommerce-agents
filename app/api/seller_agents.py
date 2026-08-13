from fastapi import APIRouter, HTTPException, status

from app.db.repositories.seller_agents import SellerAgentRepository
from app.schemas.seller_agent import SellerAgentCreate, OfferEvaluationRequest
from app.services.seller_agent_service import SellerAgentService
from app.services.ai_service import AIService

router = APIRouter(prefix="/seller-agents", tags=["seller-agents"])

# Initialize repositories and services
agent_repo = SellerAgentRepository(collection=None)
ai_service = AIService()
seller_agent_service = SellerAgentService(agent_repo, ai_service)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_seller_agent(payload: SellerAgentCreate):
    """Create a new seller agent with pricing policy."""
    try:
        result = await seller_agent_service.create_agent(payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return result


@router.get("/{agent_id}")
async def get_seller_agent(agent_id: str):
    """Retrieve a seller agent by ID."""
    try:
        result = await seller_agent_service.get_agent(agent_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return result


@router.post("/{agent_id}/evaluate-offer")
async def evaluate_offer(agent_id: str, payload: OfferEvaluationRequest):
    """Evaluate a buyer offer and return seller decision."""
    try:
        result = await seller_agent_service.evaluate_offer(agent_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return result


@router.post("/{agent_id}/increment-round")
async def increment_negotiation_round(agent_id: str):
    """Increment the negotiation round counter."""
    try:
        result = await seller_agent_service.increment_round(agent_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return result
