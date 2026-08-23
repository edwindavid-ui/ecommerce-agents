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
            # Add this right after the decision logic:
            print(f"--> SELLER AGENT DECISION: {decision} | REASON: {reason}")
            return {"decision": "reject", "reason": "Out of stock"}

        # 4. Retrieve seller policy configuration from the Seller profile
        # We assume 'agent' was already fetched at the top of the method: agent = await self.agent_repo.get_agent_by_id(agent_id)
        
        # Check both a nested 'configuration' dict or root-level agent keys depending on your schema
        policy = agent.get("configuration", {})
        
        negotiation_enabled = policy.get("negotiation_enabled", agent.get("negotiation_enabled", True))
        if not negotiation_enabled:
            await self.negotiation_service.reject_negotiation(negotiation_id)
            # Add this right after the decision logic:
            print(f"--> SELLER AGENT DECISION: {decision} | REASON: {reason}")
            return {"decision": "reject", "reason": "Negotiations are disabled for this agent."}

        offer_price = neg["current_offer"]
        
        # Set boundaries based on the agent's specific rules, falling back to product defaults if missing
        min_price = policy.get("min_price", agent.get("min_price", product.get("price", 0) * 0.75))
        target_price = policy.get("target_price", agent.get("target_price", product.get("price", 0)))
        
        product_name = product.get("title", "Item")

        # Validate internal policy boundaries
        if min_price > target_price:
            raise ValueError("Seller agent minimum price cannot be greater than target price")

        # 5. Hard Constraint: Reject immediately if below absolute minimum
        if offer_price < min_price:
            await self.negotiation_service.reject_negotiation(negotiation_id)
            await self.agent_repo.add_event(agent_id, "offer_rejected", f"Offer ₦{offer_price:,.2f} is below minimum price threshold (₦{min_price:,.2f}).")
            # Add this right after the decision logic:
            print(f"--> SELLER AGENT DECISION: {decision} | REASON: {reason}")
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
            # Add this right after the decision logic:
            print(f"--> SELLER AGENT DECISION: {decision} | REASON: {reason}")
            return {
                "decision": "accept",
                "reasoning": f"Offer ₦{offer_price:,.2f} meets or exceeds the seller's target price (₦{target_price:,.2f}).",
                "counter_price": None,
                "confidence": 1.0
            }

        # 7. Intermediate Range: Delegate to Gemini AI via AIService for intelligent negotiation reasoning
# --- 1. ALGORITHMIC GUARDRAILS (Execute BEFORE calling AI) ---
        if offer_price >= target_price:
            await self.negotiation_service.accept_offer(negotiation_id)
            await self.agent_repo.add_event(agent_id, "offer_accepted", "Offer met or exceeded target price.")
            return {"decision": "accept", "reason": "Offer met target price."}

        if offer_price < min_price:
            await self.negotiation_service.reject_negotiation(negotiation_id)
            await self.agent_repo.add_event(agent_id, "offer_rejected", "Offer was below minimum acceptable price.")
            return {"decision": "reject", "reason": "Offer below minimum threshold."}

        # --- 2. INTERMEDIATE RANGE: FORCE A COUNTER-OFFER ---
        # If we reach this line, the offer is mathematically between min and target.
        # We completely skip asking the AI "what" to do, and just ask it for a price/message.
        
        try:
            # Only ONE API call to save rate limits
            counter_result = await self.ai_service.generate_counter_offer(
                buyer_offer=offer_price,
                seller_min=min_price,
                seller_target=target_price
            )
            counter_price = counter_result.get("counter_price")
            reasoning = counter_result.get("reasoning", "Counter-offer proposed by AI agent.")
            
            # Safety check: Prevent AI hallucinations from countering below your min_price
            if not counter_price or counter_price < min_price:
                counter_price = round((offer_price + target_price) / 2, 2)
                
        except Exception as e:
            # 429 Rate Limit Fallback: If Gemini is overwhelmed, do the math instantly
            print(f"--> AI API fallback triggered: {e}", flush=True)
            counter_price = round((offer_price + target_price) / 2, 2)
            reasoning = "I can't accept the current offer, but how about this price?"

        # --- 3. DISPATCH THE OFFER ---
        counter_payload = OfferCreate(
            price=counter_price,
            message=reasoning
        )
        
        await self.negotiation_service.submit_offer(negotiation_id, sender="seller", offer=counter_payload)
        await self.agent_repo.add_event(agent_id, "counter_offer_sent", f"Counter-offer dispatched at ₦{counter_price:.2f}")

        return {
            "decision": "counter",
            "counter_price": counter_price,
            "reasoning": reasoning
        }
