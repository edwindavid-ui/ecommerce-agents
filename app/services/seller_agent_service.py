from app.db.repositories.seller_agents import SellerAgentRepository
from app.db.repositories.sellers import SellerRepository
from app.db.repositories.products import ProductRepository
from app.services.seller_service import InventoryService
from app.services.negotiation_service import NegotiationService
from app.services.ai_service import AIService
from app.schemas.seller_agent import SellerAgentCreate, OfferEvaluationRequest
from app.schemas.negotiation import OfferCreate


class SellerAgentService:
    def __init__(
        self,
        agent_repo: SellerAgentRepository,
        seller_repo: SellerRepository,
        product_repo: ProductRepository,
        inventory_service: InventoryService,
        negotiation_service: NegotiationService,
        ai_service: AIService = None
    ):
        self.agent_repo = agent_repo
        self.seller_repo = seller_repo
        self.product_repo = product_repo
        self.inventory_service = inventory_service
        self.negotiation_service = negotiation_service
        self.ai_service = ai_service or AIService()

    async def create_agent(self, seller_id: str, agent_data: SellerAgentCreate) -> dict:
        """Create a new seller agent linked to a specific seller profile."""
        existing = await self.agent_repo.get_agent_by_seller_id(seller_id)
        if existing:
            raise ValueError("Seller agent already exists for this seller profile")

        agent_dict = agent_data.model_dump()
        created = await self.agent_repo.create_agent(seller_id, agent_dict)
        return created

    async def get_agent(self, agent_id: str) -> dict:
        """Retrieve a seller agent by ID."""
        agent = await self.agent_repo.get_agent(agent_id)
        if not agent:
            raise ValueError("Seller agent not found")
        return agent

    async def respond_to_negotiation(self, agent_id: str, negotiation_id: str) -> dict:
        """
        Orchestrates the seller agent's autonomous response to an active negotiation:
        1. Validates active negotiation state and turn timing.
        2. Verifies product listing validity and inventory stock availability.
        3. Reads seller policy configuration (minimum price, target price).
        4. Enforces hard constraints (absolute minimum rejections & target price acceptances).
        5. Delegates intermediate pricing ranges to Gemini AI via AIService.
        6. Submits the final protocol decision (Accept, Counter, or Reject) via the Negotiation Service.
        """
        agent = await self.get_agent(agent_id)
        seller_id = agent["seller_id"]

        # 1. Fetch negotiation state from Negotiation Service
        neg = await self.negotiation_service.get_negotiation(negotiation_id)
        if neg["status"] != "active":
            raise ValueError(f"Negotiation is not active (status: {neg['status']})")
        
        if neg["current_turn"] != "seller":
            raise ValueError("It is not currently the seller's turn to respond.")

        # 2. Verify product details
        product = await self.product_repo.get_product(neg["product_id"])
        if not product or not product.get("is_active", True):
            await self.negotiation_service.reject_negotiation(negotiation_id)
            raise ValueError("Product is no longer active.")

        # 3. Check inventory stock levels before considering fulfillment
        inventory_docs = await self.inventory_service.inventory_repo.collection.find(
            {"product_id": neg["product_id"], "seller_id": seller_id}
        ).to_list(length=1)
        
        if not inventory_docs or inventory_docs[0].get("quantity", 0) <= 0:
            await self.negotiation_service.reject_negotiation(negotiation_id)
            await self.agent_repo.add_event(agent_id, "out_of_stock_rejection", f"Rejected negotiation {negotiation_id} due to zero inventory stock.")
            return {"decision": "reject", "reason": "Out of stock"}

        # 4. Retrieve seller policy configuration from the Seller profile
        seller = await self.seller_repo.get_seller_by_id(seller_id)
        policy = seller.get("negotiation_config", {
            "minimum_price": product.get("price", 0) * 0.75,
            "target_price": product.get("price", 0),
            "max_rounds": 5,
            "negotiation_enabled": True
        })

        if not policy.get("negotiation_enabled", True):
            await self.negotiation_service.reject_negotiation(negotiation_id)
            return {"decision": "reject", "reason": "Negotiations are disabled for this seller."}

        offer_price = neg["current_offer"]
        min_price = policy.get("minimum_price", product.get("price", 0) * 0.75)
        target_price = policy.get("target_price", product.get("price", 0))
        product_name = product.get("title", "Item")

        # Validate internal policy boundaries
        if min_price > target_price:
            raise ValueError("Seller minimum price cannot be greater than target price")

        # 5. Hard Constraint: Reject immediately if below absolute minimum
        if offer_price < min_price:
            await self.negotiation_service.reject_negotiation(negotiation_id)
            await self.agent_repo.add_event(agent_id, "offer_rejected", f"Offer ₦{offer_price:,.2f} is below minimum price threshold (₦{min_price:,.2f}).")
            return {
                "decision": "reject",
                "reasoning": f"Offer ₦{offer_price:,.2f} is below the absolute minimum acceptable price (₦{min_price:,.2f}).",
                "counter_price": None,
                "confidence": 1.0
            }

        # 6. Hard Constraint: Accept immediately if it meets or exceeds target price
        if offer_price >= target_price:
            await self.negotiation_service.accept_offer(negotiation_id)
            await self.agent_repo.add_event(agent_id, "offer_accepted", f"Offer ₦{offer_price:,.2f} meets or exceeds target price (₦{target_price:,.2f}).")
            return {
                "decision": "accept",
                "reasoning": f"Offer ₦{offer_price:,.2f} meets or exceeds the seller's target price (₦{target_price:,.2f}).",
                "counter_price": None,
                "confidence": 1.0
            }

        # 7. Intermediate Range: Delegate to Gemini AI via AIService for intelligent negotiation reasoning
        ai_evaluation = await self.ai_service.evaluate_offer_as_seller(
            offer_price=offer_price,
            min_price=min_price,
            product_name=product_name
        )

        # If Gemini decides to counter, generate and dispatch the counter-offer
        if ai_evaluation.get("decision") == "counter":
            counter_result = await self.ai_service.generate_counter_offer(
                buyer_offer=offer_price,
                seller_min=min_price,
                seller_target=target_price
            )
            counter_price = counter_result.get("counter_price", round((offer_price + target_price) / 2, 2))
            
            counter_payload = OfferCreate(
                price=counter_price, 
                message=counter_result.get("reasoning", "Counter-offer proposed by AI agent.")
            )
            await self.negotiation_service.submit_offer(negotiation_id, sender="seller", offer=counter_payload)
            await self.agent_repo.add_event(agent_id, "counter_offer_sent", f"Counter-offer dispatched at ₦{counter_price:,.2f}")
            
            return {
                "decision": "counter",
                "counter_price": counter_price,
                "reasoning": counter_result.get("reasoning")
            }

        elif ai_evaluation.get("decision") == "accept":
            await self.negotiation_service.accept_offer(negotiation_id)
            await self.agent_repo.add_event(agent_id, "offer_accepted", "AI evaluated and accepted offer.")
            return ai_evaluation
        else:
            await self.negotiation_service.reject_negotiation(negotiation_id)
            await self.agent_repo.add_event(agent_id, "offer_rejected", "AI evaluated and rejected offer.")
            return ai_evaluation