from fastapi import APIRouter, HTTPException, status
from app.db.mongodb import database

from app.db.repositories.buyer_agents import BuyerTaskRepository, BuyerAgentStateRepository
from app.db.repositories.recommendations import RecommendationRepository
from app.services.buyer_agent_service import BuyerAgentService
from app.db.repositories.products import ProductRepository
from app.db.repositories.sellers import InventoryRepository
from app.services.recommendation_service import RecommendationService
from app.services.ai_service import AIService
from app.schemas.buyer_agent import BuyerAgentCreate
from fastapi import Depends
from app.auth.deps import get_current_user_id


router = APIRouter(prefix="/buyer-agents", tags=["buyer-agents"])

product_repo = ProductRepository(collection=database.get_collection("products"))
inventory_repo = InventoryRepository(collection=database.get_collection("inventory"))
rec_repo = RecommendationRepository(collection=database.get_collection("recommendations"))
ai_service = AIService()
task_repo = BuyerTaskRepository(collection=database.get_collection("buyer_tasks"))
buyer_agent_repo = task_repo
state_repo = BuyerAgentStateRepository(collection=database.get_collection("buyer_agents"))

rec_service = RecommendationService(
    product_repo=product_repo,
    inventory_repo=inventory_repo,
    recommendation_repo=rec_repo,
    ai_service=ai_service
)
ai_service = AIService()
buyer_agent_service = BuyerAgentService(task_repo, state_repo, rec_service, ai_service)

# --- Routes ---
@router.post("/buyer-agents", status_code=status.HTTP_201_CREATED)
async def create_buyer_agent(payload: BuyerAgentCreate, current_user_id: str = Depends(get_current_user_id)):
    """
    Initialize a new autonomous buyer agent with an objective, budget boundaries, and preferences.
    """
    try:
        agent_dict = payload.model_dump()
        created = await buyer_agent_repo.create_agent(current_user_id, agent_dict)
        return {
            "message": "Buyer agent initialized successfully",
            "agent": created
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Failed to create buyer agent: {str(exc)}")


@router.get("/buyer-agents/{agent_id}", status_code=status.HTTP_200_OK)
async def get_buyer_agent(agent_id: str):
    """
    Retrieve the current status, selected products, and event history of a specific buyer agent.
    """
    agent = await buyer_agent_repo.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Buyer agent not found")
        
    return {"agent": agent}

@router.post("/buyer-agents/{agent_id}/recommend", status_code=status.HTTP_200_OK)
async def trigger_agent_recommendation(agent_id: str):
    """
    Trigger the buyer agent to execute its recommendation stage, 
    evaluating in-stock products and selecting its top candidate.
    """
    try:
        result = await buyer_agent_service.recommend_for_agent(agent_id)
        return result
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Agent recommendation stage failed: {str(exc)}")