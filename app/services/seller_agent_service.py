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
            Evaluate a buyer offer using backend hard rules for boundaries,
            and Gemini AI via AIService for intelligent decision-making and counter-offers.
            """
            agent = await self.agent_repo.get_agent_by_id(agent_id)
            if not agent:
                raise ValueError("Seller agent not found")

            offer_price = offer_request.offer_price
            min_price = agent["min_price"]
            target_price = agent["target_price"]
            product_name = agent.get("product_id", "Item")

            # 1. Hard Constraint: Reject immediately if below absolute minimum
            if offer_price < min_price:
                return {
                    "decision": "reject",
                    "reasoning": f"Offer ${offer_price} is below the absolute minimum acceptable price (${min_price}).",
                    "counter_price": None,
                    "confidence": 1.0
                }

            # 2. Hard Constraint: Accept immediately if it meets or exceeds target
            if offer_price >= target_price:
                return {
                    "decision": "accept",
                    "reasoning": f"Offer ${offer_price} meets or exceeds the seller's target price (${target_price}).",
                    "counter_price": None,
                    "confidence": 1.0
                }

            # 3. Intermediate Range: Delegate to Gemini AI via AIService for intelligent negotiation
            ai_evaluation = await self.ai_service.evaluate_offer_as_seller(
                offer_price=offer_price,
                min_price=min_price,
                product_name=product_name
            )

            # If Gemini decides to counter, call the counter-offer service method
            if ai_evaluation.get("decision") == "counter":
                counter_result = await self.ai_service.generate_counter_offer(
                    buyer_offer=offer_price,
                    seller_min=min_price,
                    seller_target=target_price
                )
                return counter_result

            return ai_evaluation

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
