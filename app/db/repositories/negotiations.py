from datetime import datetime, timezone
from typing import Any, Optional

from app.schemas.negotiation import NegotiationCreate


class NegotiationRepository:
    def __init__(self, collection: Any):
        self.collection = collection
        self._negotiations: dict[str, dict] = {}
        self._messages: dict[str, list[dict]] = {}

    async def create_negotiation(self, neg_data: NegotiationCreate) -> dict:
        neg_id = f"neg_{len(self._negotiations) + 1}"
        now = datetime.now(timezone.utc).isoformat()
        
        negotiation = {
            "id": neg_id,
            "buyer_id": neg_data.buyer_id,
            "seller_id": neg_data.seller_id,
            "product_id": neg_data.product_id,
            "buyer_max_price": neg_data.buyer_max_price,
            "seller_min_price": neg_data.seller_min_price,
            "seller_target_price": neg_data.seller_target_price,
            "max_rounds": neg_data.max_rounds,
            "status": "initiated",
            "current_round": 0,
            "current_offer": None,
            "final_price": None,
            "created_at": now,
            "updated_at": now,
        }
        self._negotiations[neg_id] = negotiation
        self._messages[neg_id] = []
        return negotiation

    async def get_negotiation_by_id(self, negotiation_id: str) -> Optional[dict]:
        return self._negotiations.get(negotiation_id)

    async def update_negotiation_status(self, negotiation_id: str, status: str) -> Optional[dict]:
        neg = self._negotiations.get(negotiation_id)
        if not neg:
            return None
        neg["status"] = status
        neg["updated_at"] = datetime.now(timezone.utc).isoformat()
        return neg

    async def update_negotiation_offer(self, negotiation_id: str, offer_price: float, round_num: int) -> Optional[dict]:
        neg = self._negotiations.get(negotiation_id)
        if not neg:
            return None
        neg["current_offer"] = offer_price
        neg["current_round"] = round_num
        neg["updated_at"] = datetime.now(timezone.utc).isoformat()
        return neg

    async def set_final_price(self, negotiation_id: str, final_price: float) -> Optional[dict]:
        neg = self._negotiations.get(negotiation_id)
        if not neg:
            return None
        neg["final_price"] = final_price
        neg["updated_at"] = datetime.now(timezone.utc).isoformat()
        return neg

    async def add_message(self, negotiation_id: str, message: dict) -> Optional[dict]:
        if negotiation_id not in self._messages:
            return None
        self._messages[negotiation_id].append(message)
        return message

    async def get_messages(self, negotiation_id: str) -> list[dict]:
        return self._messages.get(negotiation_id, [])

    async def list_negotiations_by_buyer(self, buyer_id: str) -> list[dict]:
        return [n for n in self._negotiations.values() if n["buyer_id"] == buyer_id]

    async def list_negotiations_by_seller(self, seller_id: str) -> list[dict]:
        return [n for n in self._negotiations.values() if n["seller_id"] == seller_id]
