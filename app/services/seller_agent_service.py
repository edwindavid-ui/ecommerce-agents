from app.db.repositories.seller_agents import SellerAgentRepository
from app.schemas.seller_agent import SellerAgentCreate, OfferEvaluationRequest, OfferEvaluationResult
from app.services.ai_service import AIService


class SellerAgentService:
    def __init__(self, agent_repo: SellerAgentRepository, ai_service: AIService = None):
        self.agent_repo = agent_repo
        self.ai_service = ai_service or AIService()

    async def create_agent(self, agent_data: SellerAgentCreate) -> dict:
        """Create a new seller agent with pricing policy."""
        # Validate pricing constraints
        if agent_data.min_price > agent_data.target_price:
            raise ValueError("min_price cannot be greater than target_price")
        if agent_data.target_price > agent_data.list_price:
            raise ValueError("target_price cannot be greater than list_price")
        
        agent = await self.agent_repo.create_agent(agent_data)
        
        return {
            "agent_id": agent["id"],
            "seller_id": agent["seller_id"],
            "product_id": agent["product_id"],
            "list_price": agent["list_price"],
            "min_price": agent["min_price"],
            "target_price": agent["target_price"],
            "max_negotiation_rounds": agent["max_negotiation_rounds"],
            "current_round": agent["current_round"],
            "status": agent["status"],
        }

    async def get_agent(self, agent_id: str) -> dict:
        """Retrieve a seller agent by ID."""
        agent = await self.agent_repo.get_agent_by_id(agent_id)
        if not agent:
            raise ValueError("Seller agent not found")
        
        return {
            "agent_id": agent["id"],
            "seller_id": agent["seller_id"],
            "product_id": agent["product_id"],
            "list_price": agent["list_price"],
            "min_price": agent["min_price"],
            "target_price": agent["target_price"],
            "max_negotiation_rounds": agent["max_negotiation_rounds"],
            "current_round": agent["current_round"],
            "status": agent["status"],
        }

    async def evaluate_offer(self, agent_id: str, offer_request: OfferEvaluationRequest) -> dict:
        """
        Evaluate a buyer offer using seller policy and AI reasoning.
        Backend enforces pricing constraints strictly.
        """
        agent = await self.agent_repo.get_agent_by_id(agent_id)
        if not agent:
            raise ValueError("Seller agent not found")
        
        offer_price = offer_request.offer_price
        min_price = agent["min_price"]
        target_price = agent["target_price"]
        
        # Rule 1: Offer must not be below minimum (hard constraint)
        if offer_price < min_price:
            decision = "reject"
            reasoning = f"Offer ${offer_price} is below minimum acceptable price ${min_price}"
            return {
                "decision": decision,
                "reasoning": reasoning,
                "counter_price": None,
                "confidence": 0.95,
            }
        
        # Rule 2: Offer meets or exceeds target - accept
        if offer_price >= target_price:
            decision = "accept"
            reasoning = f"Offer ${offer_price} meets or exceeds target price ${target_price}"
            return {
                "decision": decision,
                "reasoning": reasoning,
                "counter_price": None,
                "confidence": 0.95,
            }
        
        # Rule 3: Offer is between min and target - counter
        if min_price <= offer_price < target_price:
            # Calculate counter price as midpoint, capped to ensure it's above min
            counter_price = max((offer_price + target_price) / 2, min_price + 1.0)
            decision = "counter"
            reasoning = f"Offer ${offer_price} is acceptable but below target. Countering with ${counter_price:.2f}"
            return {
                "decision": decision,
                "reasoning": reasoning,
                "counter_price": round(counter_price, 2),
                "confidence": 0.85,
            }
        
        # Default: reject
        decision = "reject"
        reasoning = "Unable to evaluate offer"
        return {
            "decision": decision,
            "reasoning": reasoning,
            "counter_price": None,
            "confidence": 0.5,
        }

    async def increment_round(self, agent_id: str) -> dict:
        """Increment negotiation round counter."""
        agent = await self.agent_repo.get_agent_by_id(agent_id)
        if not agent:
            raise ValueError("Seller agent not found")
        
        new_round = agent["current_round"] + 1
        if new_round > agent["max_negotiation_rounds"]:
            await self.agent_repo.update_agent_status(agent_id, "negotiation_expired")
            raise ValueError("Maximum negotiation rounds exceeded")
        
        agent = await self.agent_repo.update_agent_round(agent_id, new_round)
        
        return {
            "agent_id": agent["id"],
            "seller_id": agent["seller_id"],
            "product_id": agent["product_id"],
            "list_price": agent["list_price"],
            "min_price": agent["min_price"],
            "target_price": agent["target_price"],
            "max_negotiation_rounds": agent["max_negotiation_rounds"],
            "current_round": agent["current_round"],
            "status": agent["status"],
        }
