from app.db.repositories.buyer_agents import BuyerTaskRepository, BuyerAgentStateRepository
from app.db.repositories.recommendations import RecommendationRepository
from app.schemas.buyer_agent import BuyerTaskCreate, BuyerAgentState
from app.schemas.recommendation import RecommendationRequest
from app.services.ai_service import AIService
from app.services.recommendation_service import RecommendationService

class BuyerAgentService:
    def __init__(self, task_repo, state_repo, recommendation_service, ai_service):
        self.task_repo = task_repo
        self.state_repo = state_repo
        self.buyer_agent_repo = task_repo  
        self.recommendation_service = recommendation_service
        self.ai_service = ai_service

    async def recommend_for_agent(self, agent_id: str) -> dict:
        agent = await self.buyer_agent_repo.get_agent(agent_id)
        if not agent:
            raise ValueError("Buyer agent not found")

        # 1. Map agent parameters into a RecommendationRequest
        req = RecommendationRequest(
            query=agent.get("objective"),
            category=agent.get("category"),
            min_price=agent.get("min_budget"),
            max_price=agent.get("max_budget"),
            preferences=agent.get("preferences", {}),
            limit=5
        )

        # 2. Call the Recommendation Service (which filters by catalog, inventory, and AI ranking)
        rec_response = await self.recommendation_service.recommend(req, buyer_id=agent.get("user_id", "system"))
        results = rec_response.results

        if not results:
            await self.buyer_agent_repo.update_status(agent_id, "failed")
            await self.buyer_agent_repo.add_event(
                agent_id, 
                "recommendation_failed", 
                "No active products matched the agent's budget criteria and inventory availability."
            )
            return {"message": "No matching products found", "recommendations": []}

        # 3. Select the top candidate (highest AI score)
        top_candidate = results[0]

        # 4. Update agent state to 'evaluating' and store the targeted product/seller IDs
        await self.buyer_agent_repo.update_status(
            agent_id, 
            status="evaluating",
            extra_updates={
                "current_product_id": top_candidate.product_id,
                "current_seller_id": top_candidate.seller_id
            }
        )
        
        # 5. Log the decision event for auditability
        await self.buyer_agent_repo.add_event(
            agent_id, 
            "product_selected", 
            f"Selected top product {top_candidate.product_id} from seller {top_candidate.seller_id} with score {top_candidate.score}"
        )

        return {
            "message": "Recommendations retrieved and top product selected successfully",
            "top_candidate": top_candidate.model_dump(),
            "all_recommendations": [r.model_dump() for r in results]
        }