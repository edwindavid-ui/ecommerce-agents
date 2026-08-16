from app.schemas.negotiation import NegotiationCreate, OfferCreate

class NegotiationService:
    def __init__(self, negotiation_repo, seller_agent_service=None):
        self.negotiation_repo = negotiation_repo
        self.seller_agent_service = seller_agent_service

    async def start_negotiation(self, payload: NegotiationCreate) -> dict:
        # Note: In a full flow, you'd verify the product_id and seller_id exist here.
        neg_dict = payload.model_dump()
        neg_dict["current_offer"] = payload.initial_offer
        return await self.negotiation_repo.create(neg_dict)

    async def get_negotiation(self, neg_id: str) -> dict:
        neg = await self.negotiation_repo.get_by_id(neg_id)
        if not neg:
            raise ValueError("Negotiation not found")
        return neg

    async def submit_offer(self, neg_id: str, sender: str, offer: OfferCreate) -> dict:
        neg = await self.get_negotiation(neg_id)

        # Rule 1: Must be active
        if neg["status"] != "active":
            raise ValueError(f"Negotiation is {neg['status']} and cannot accept new offers.")

        # Rule 2: Strict turn-taking
        if neg["current_turn"] != sender:
            raise ValueError(f"It is not {sender}'s turn to make an offer.")

        # Rule 3: Enforce round limits
        if neg["round"] >= neg["max_rounds"]:
            await self.negotiation_repo.update_status(neg_id, "expired")
            raise ValueError("Maximum negotiation rounds reached. Negotiation expired.")

        # Calculate next state
        new_round = neg["round"] + 1
        next_turn = "buyer" if sender == "seller" else "seller"

        # Save offer
        updated_neg = await self.negotiation_repo.add_offer(
            neg_id, sender, offer.price, offer.message, new_round, next_turn
        )
        return updated_neg

    async def accept_offer(self, neg_id: str) -> dict:
        neg = await self.get_negotiation(neg_id)
        if neg["status"] != "active":
            raise ValueError(f"Cannot accept a negotiation that is {neg['status']}.")

        return await self.negotiation_repo.update_status(
            neg_id, status="accepted", final_price=neg["current_offer"]
        )

    async def reject_negotiation(self, neg_id: str) -> dict:
        neg = await self.get_negotiation(neg_id)
        if neg["status"] != "active":
            raise ValueError(f"Cannot reject a negotiation that is {neg['status']}.")

        return await self.negotiation_repo.update_status(neg_id, status="rejected")

    async def cancel_negotiation(self, neg_id: str) -> dict:
        neg = await self.get_negotiation(neg_id)
        if neg["status"] not in ["active", "pending"]:
            raise ValueError(f"Cannot cancel a negotiation that is already {neg['status']}.")

        return await self.negotiation_repo.update_status(neg_id, status="cancelled")
  