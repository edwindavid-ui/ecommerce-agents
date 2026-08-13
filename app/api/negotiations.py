from fastapi import APIRouter, HTTPException, status

from app.db.repositories import negotiation_repo, seller_agent_repo
from app.schemas.negotiation import NegotiationCreate, OfferRequest
from app.services.negotiation_service import NegotiationService
from app.services.seller_agent_service import SellerAgentService

router = APIRouter(prefix="/negotiations", tags=["negotiations"])

# Initialize services with shared repositories
seller_agent_service = SellerAgentService(seller_agent_repo)
negotiation_service = NegotiationService(negotiation_repo, seller_agent_service)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_negotiation(payload: NegotiationCreate):
    """Create a new negotiation between buyer and seller."""
    try:
        result = await negotiation_service.create_negotiation(payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return result


@router.get("/{negotiation_id}")
async def get_negotiation(negotiation_id: str):
    """Retrieve a negotiation by ID."""
    try:
        result = await negotiation_service.get_negotiation(negotiation_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return result


@router.post("/{negotiation_id}/offer")
async def make_offer(negotiation_id: str, payload: OfferRequest):
    """Make an offer in a negotiation."""
    try:
        result = await negotiation_service.make_offer(negotiation_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return result


@router.get("/{negotiation_id}/messages")
async def get_negotiation_messages(negotiation_id: str):
    """Get all messages in a negotiation."""
    try:
        messages = await negotiation_service.get_negotiation_messages(negotiation_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return {"negotiation_id": negotiation_id, "messages": messages}
