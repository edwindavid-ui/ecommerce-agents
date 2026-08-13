from datetime import datetime, timezone

from app.db.repositories.negotiations import NegotiationRepository
from app.schemas.negotiation import NegotiationCreate, OfferRequest
from app.services.seller_agent_service import SellerAgentService
from app.db.repositories.seller_agents import SellerAgentRepository
from app.schemas.seller_agent import OfferEvaluationRequest


class NegotiationService:
    def __init__(
        self,
        neg_repo: NegotiationRepository,
        seller_agent_service: SellerAgentService = None,
    ):
        self.neg_repo = neg_repo
        self.seller_agent_service = seller_agent_service

    async def create_negotiation(self, neg_data: NegotiationCreate) -> dict:
        """Create a new negotiation between buyer and seller."""
        # Validate constraints
        if neg_data.seller_min_price > neg_data.buyer_max_price:
            raise ValueError("Negotiation impossible: seller minimum exceeds buyer maximum")
        
        neg = await self.neg_repo.create_negotiation(neg_data)
        
        return {
            "negotiation_id": neg["id"],
            "buyer_id": neg["buyer_id"],
            "seller_id": neg["seller_id"],
            "product_id": neg["product_id"],
            "buyer_max_price": neg["buyer_max_price"],
            "seller_min_price": neg["seller_min_price"],
            "seller_target_price": neg["seller_target_price"],
            "status": neg["status"],
            "current_round": neg["current_round"],
            "current_offer": neg["current_offer"],
            "final_price": neg["final_price"],
            "created_at": neg["created_at"],
            "updated_at": neg["updated_at"],
        }

    async def get_negotiation(self, negotiation_id: str) -> dict:
        """Retrieve a negotiation by ID."""
        neg = await self.neg_repo.get_negotiation_by_id(negotiation_id)
        if not neg:
            raise ValueError("Negotiation not found")
        
        return {
            "negotiation_id": neg["id"],
            "buyer_id": neg["buyer_id"],
            "seller_id": neg["seller_id"],
            "product_id": neg["product_id"],
            "buyer_max_price": neg["buyer_max_price"],
            "seller_min_price": neg["seller_min_price"],
            "seller_target_price": neg["seller_target_price"],
            "status": neg["status"],
            "current_round": neg["current_round"],
            "current_offer": neg["current_offer"],
            "final_price": neg["final_price"],
            "created_at": neg["created_at"],
            "updated_at": neg["updated_at"],
        }

    async def make_offer(self, negotiation_id: str, offer_request: OfferRequest) -> dict:
        """
        Process an offer in a negotiation.
        Enforces seller pricing constraints and buyer budget constraints.
        """
        neg = await self.neg_repo.get_negotiation_by_id(negotiation_id)
        if not neg:
            raise ValueError("Negotiation not found")
        
        # Check if negotiation is still active
        if neg["status"] not in ["initiated", "offered", "countered"]:
            raise ValueError(f"Cannot make offer in status: {neg['status']}")
        
        # Check round limit
        if neg["current_round"] >= neg["max_rounds"]:
            await self.neg_repo.update_negotiation_status(negotiation_id, "expired")
            raise ValueError("Maximum negotiation rounds reached")
        
        offer_price = offer_request.offer_price
        
        # Validate buyer constraint
        if offer_request.actor == "buyer":
            if offer_price > neg["buyer_max_price"]:
                raise ValueError(f"Offer {offer_price} exceeds buyer maximum {neg['buyer_max_price']}")
        
        # Validate seller constraint
        if offer_request.actor == "seller":
            if offer_price < neg["seller_min_price"]:
                raise ValueError(f"Offer {offer_price} below seller minimum {neg['seller_min_price']}")
        
        # Update offer in negotiation
        new_round = neg["current_round"] + 1
        await self.neg_repo.update_negotiation_offer(negotiation_id, offer_price, new_round)
        
        # Log the message
        message = {
            "message_id": f"msg_{new_round}",
            "negotiation_id": negotiation_id,
            "actor": offer_request.actor,
            "message_type": "offer",
            "offer_price": offer_price,
            "reasoning": f"{offer_request.actor.capitalize()} offers ${offer_price:.2f}",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        await self.neg_repo.add_message(negotiation_id, message)
        
        # Evaluate offer using seller agent rules
        decision = await self._evaluate_offer(neg, offer_price)
        
        # Update status based on decision
        if decision["decision"] == "accept":
            await self.neg_repo.update_negotiation_status(negotiation_id, "accepted")
            await self.neg_repo.set_final_price(negotiation_id, offer_price)
        elif decision["decision"] == "counter":
            await self.neg_repo.update_negotiation_status(negotiation_id, "countered")
        elif decision["decision"] == "reject":
            await self.neg_repo.update_negotiation_status(negotiation_id, "rejected")
        
        # Get updated negotiation
        neg = await self.neg_repo.get_negotiation_by_id(negotiation_id)
        
        return {
            "negotiation_id": neg["id"],
            "buyer_id": neg["buyer_id"],
            "seller_id": neg["seller_id"],
            "product_id": neg["product_id"],
            "buyer_max_price": neg["buyer_max_price"],
            "seller_min_price": neg["seller_min_price"],
            "seller_target_price": neg["seller_target_price"],
            "status": neg["status"],
            "current_round": neg["current_round"],
            "current_offer": neg["current_offer"],
            "final_price": neg["final_price"],
            "created_at": neg["created_at"],
            "updated_at": neg["updated_at"],
            "last_decision": decision,
        }

    async def _evaluate_offer(self, negotiation: dict, offer_price: float) -> dict:
        """Evaluate an offer using deterministic seller rules."""
        min_price = negotiation["seller_min_price"]
        target_price = negotiation["seller_target_price"]
        
        # Rule 1: Offer below minimum
        if offer_price < min_price:
            return {
                "decision": "reject",
                "reasoning": f"Offer ${offer_price} below minimum ${min_price}",
            }
        
        # Rule 2: Offer at or above target
        if offer_price >= target_price:
            return {
                "decision": "accept",
                "reasoning": f"Offer ${offer_price} meets or exceeds target ${target_price}",
            }
        
        # Rule 3: Offer between min and target
        if min_price <= offer_price < target_price:
            counter_price = max((offer_price + target_price) / 2, min_price + 1.0)
            return {
                "decision": "counter",
                "reasoning": f"Offer ${offer_price} countered with ${counter_price:.2f}",
                "counter_price": round(counter_price, 2),
            }
        
        return {
            "decision": "reject",
            "reasoning": "Unable to evaluate offer",
        }

    async def get_negotiation_messages(self, negotiation_id: str) -> list[dict]:
        """Retrieve all messages in a negotiation."""
        neg = await self.neg_repo.get_negotiation_by_id(negotiation_id)
        if not neg:
            raise ValueError("Negotiation not found")
        
        return await self.neg_repo.get_messages(negotiation_id)
