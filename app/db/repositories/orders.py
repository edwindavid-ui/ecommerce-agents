from datetime import datetime, timezone
from typing import Any, Optional

from app.schemas.order import OrderCreate


class OrderRepository:
    def __init__(self, collection: Any):
        self.collection = collection
        self._orders: dict[str, dict] = {}

    async def create_order(self, order_data: OrderCreate, negotiation: dict) -> dict:
        """Create an order from an accepted negotiation."""
        order_id = f"order_{len(self._orders) + 1}"
        now = datetime.now(timezone.utc).isoformat()
        
        order = {
            "id": order_id,
            "negotiation_id": order_data.negotiation_id,
            "buyer_id": negotiation["buyer_id"],
            "seller_id": negotiation["seller_id"],
            "product_id": negotiation["product_id"],
            "final_price": negotiation["final_price"],
            "status": "pending",
            "created_at": now,
            "updated_at": now,
        }
        self._orders[order_id] = order
        return order

    async def get_order_by_id(self, order_id: str) -> Optional[dict]:
        return self._orders.get(order_id)

    async def update_order_status(self, order_id: str, status: str) -> Optional[dict]:
        order = self._orders.get(order_id)
        if not order:
            return None
        order["status"] = status
        order["updated_at"] = datetime.now(timezone.utc).isoformat()
        return order

    async def list_orders_by_buyer(self, buyer_id: str) -> list[dict]:
        return [o for o in self._orders.values() if o["buyer_id"] == buyer_id]

    async def list_orders_by_seller(self, seller_id: str) -> list[dict]:
        return [o for o in self._orders.values() if o["seller_id"] == seller_id]

    async def list_all_orders(self) -> list[dict]:
        return list(self._orders.values())
