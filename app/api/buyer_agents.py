from fastapi import APIRouter, HTTPException, status

from app.db.repositories.buyer_agents import BuyerTaskRepository, BuyerAgentStateRepository
from app.db.repositories.recommendations import RecommendationRepository
from app.schemas.buyer_agent import BuyerTaskCreate
from app.services.buyer_agent_service import BuyerAgentService
from app.services.recommendation_service import RecommendationService
from app.services.ai_service import AIService

router = APIRouter(prefix="/buyer-agents", tags=["buyer-agents"])

# Initialize repositories and services
# In a real app, these would come from dependency injection and use real MongoDB
task_repo = BuyerTaskRepository(collection=None)
state_repo = BuyerAgentStateRepository(collection=None)
rec_repo = RecommendationRepository(collection=None)

from app.db.repositories.products import ProductRepository
product_repo = ProductRepository(collection=None)

rec_service = RecommendationService(product_repo, rec_repo)
ai_service = AIService()
buyer_agent_service = BuyerAgentService(task_repo, state_repo, rec_service, ai_service)


@router.post("/tasks", status_code=status.HTTP_201_CREATED)
async def create_buyer_task(payload: BuyerTaskCreate):
    """Create a new buyer agent task."""
    try:
        result = await buyer_agent_service.create_task(payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return result


@router.get("/tasks/{task_id}")
async def get_buyer_task(task_id: str):
    """Retrieve a buyer agent task by ID."""
    try:
        result = await buyer_agent_service.get_task(task_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return result


@router.post("/tasks/{task_id}/start")
async def start_buyer_task(task_id: str):
    """Start a buyer agent task."""
    try:
        result = await buyer_agent_service.start_task(task_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc
    return result


@router.post("/tasks/{task_id}/cancel")
async def cancel_buyer_task(task_id: str):
    """Cancel a buyer agent task."""
    try:
        result = await buyer_agent_service.cancel_task(task_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return result
