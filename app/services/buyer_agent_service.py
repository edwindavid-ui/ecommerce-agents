from app.db.repositories.buyer_agents import BuyerTaskRepository, BuyerAgentStateRepository
from app.db.repositories.recommendations import RecommendationRepository
from app.schemas.buyer_agent import BuyerTaskCreate, BuyerAgentState
from app.schemas.recommendation import RecommendationRequest
from app.services.ai_service import AIService
from app.services.recommendation_service import RecommendationService


class BuyerAgentService:
    def __init__(
        self,
        task_repo: BuyerTaskRepository,
        state_repo: BuyerAgentStateRepository,
        rec_service: RecommendationService,
        ai_service: AIService,
    ):
        self.task_repo = task_repo
        self.state_repo = state_repo
        self.rec_service = rec_service
        self.ai_service = ai_service

    async def create_task(self, task_data: BuyerTaskCreate) -> dict:
        """Create a new buyer task."""
        task = await self.task_repo.create_task(task_data)
        
        # Initialize agent state
        state = BuyerAgentState(
            task_id=task["id"],
            state="TASK_CREATED",
        )
        await self.state_repo.save_state(task["id"], state)
        
        return {
            "task_id": task["id"],
            "buyer_id": task["buyer_id"],
            "requirement": task["requirement"],
            "budget": task["budget"],
            "category": task["category"],
            "status": task["status"],
            "selected_seller_id": task["selected_seller_id"],
            "selected_product_id": task["selected_product_id"],
            "recommendation_id": task["recommendation_id"],
            "created_at": task["created_at"],
            "updated_at": task["updated_at"],
        }

    async def get_task(self, task_id: str) -> dict:
        """Retrieve a task by ID."""
        task = await self.task_repo.get_task_by_id(task_id)
        if not task:
            raise ValueError("Task not found")
        
        return {
            "task_id": task["id"],
            "buyer_id": task["buyer_id"],
            "requirement": task["requirement"],
            "budget": task["budget"],
            "category": task["category"],
            "status": task["status"],
            "selected_seller_id": task["selected_seller_id"],
            "selected_product_id": task["selected_product_id"],
            "recommendation_id": task["recommendation_id"],
            "created_at": task["created_at"],
            "updated_at": task["updated_at"],
        }

    async def start_task(self, task_id: str) -> dict:
        """Start a buyer agent task through its lifecycle."""
        task = await self.task_repo.get_task_by_id(task_id)
        if not task:
            raise ValueError("Task not found")
        
        state = await self.state_repo.get_state(task_id)
        
        # State transitions: TASK_CREATED → ANALYZING_REQUIREMENTS → SEARCHING → EVALUATING_PRODUCTS
        if task["status"] == "task_created":
            # ANALYZING_REQUIREMENTS
            await self.task_repo.update_task_status(task_id, "analyzing_requirements")
            
            # Use AI to understand requirements
            try:
                analysis = await self.ai_service.analyze_products_for_buyer(
                    requirement=task["requirement"],
                    candidates=[]  # No candidates yet
                )
            except Exception:
                analysis = {}
            
            if state:
                state["analysis_result"] = analysis
                state["state"] = "ANALYZING_REQUIREMENTS"
            
            # Move to SEARCHING
            await self.task_repo.update_task_status(task_id, "searching")
            
            # Generate recommendations
            try:
                rec_request = RecommendationRequest(
                    buyer_id=task["buyer_id"],
                    category=task["category"],
                    max_price=task["budget"],
                    min_price=task.get("min_price"),
                )
                rec_result = await self.rec_service.generate_recommendations(
                    buyer_id=task["buyer_id"],
                    request=rec_request,
                )
                rec_id = rec_result.get("recommendation_id")
                candidates = rec_result.get("results", [])
            except Exception:
                rec_id = None
                candidates = []
            
            if rec_id:
                await self.task_repo.update_task_with_recommendation(task_id, rec_id)
            
            if state:
                state["product_candidates"] = candidates
                state["recommendation_id"] = rec_id
                state["state"] = "EVALUATING_PRODUCTS"
            
            # Move to EVALUATING_PRODUCTS
            await self.task_repo.update_task_status(task_id, "evaluating_products")
            
            # If candidates exist, evaluate them
            if candidates:
                best_product = candidates[0]
                product_id = best_product.get("product_id")
                seller_id = best_product.get("seller_id")
                
                if state:
                    state["selected_product_id"] = product_id
                    state["selected_seller_id"] = seller_id
                
                await self.task_repo.update_task_status(task_id, "completed")
            else:
                await self.task_repo.update_task_status(task_id, "completed")
            
            if state:
                state["state"] = "COMPLETED"
                await self.state_repo.save_state(task_id, BuyerAgentState(**state))
        
        task = await self.task_repo.get_task_by_id(task_id)
        
        return {
            "task_id": task["id"],
            "buyer_id": task["buyer_id"],
            "requirement": task["requirement"],
            "budget": task["budget"],
            "category": task["category"],
            "status": task["status"],
            "selected_seller_id": task["selected_seller_id"],
            "selected_product_id": task["selected_product_id"],
            "recommendation_id": task["recommendation_id"],
            "created_at": task["created_at"],
            "updated_at": task["updated_at"],
        }

    async def cancel_task(self, task_id: str) -> dict:
        """Cancel a buyer task."""
        task = await self.task_repo.get_task_by_id(task_id)
        if not task:
            raise ValueError("Task not found")
        
        task = await self.task_repo.update_task_status(task_id, "cancelled")
        state = await self.state_repo.get_state(task_id)
        if state:
            state["state"] = "CANCELLED"
            await self.state_repo.save_state(task_id, BuyerAgentState(**state))
        
        return {
            "task_id": task["id"],
            "buyer_id": task["buyer_id"],
            "requirement": task["requirement"],
            "budget": task["budget"],
            "category": task["category"],
            "status": task["status"],
            "selected_seller_id": task["selected_seller_id"],
            "selected_product_id": task["selected_product_id"],
            "recommendation_id": task["recommendation_id"],
            "created_at": task["created_at"],
            "updated_at": task["updated_at"],
        }
