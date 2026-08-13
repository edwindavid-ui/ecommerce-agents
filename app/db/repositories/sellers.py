from typing import Any, Optional

from app.schemas.seller import SellerCreate


class SellerRepository:
    def __init__(self, collection: Any):
        self.collection = collection
        self._sellers: dict[str, dict] = {}

    async def create_seller(self, user_id: str, seller_data: SellerCreate) -> dict:
        seller = {
            "id": f"seller_{len(self._sellers) + 1}",
            "user_id": user_id,
            "business_name": seller_data.business_name,
            "description": seller_data.description,
            "rating": 0.0,
            "status": "active",
        }
        self._sellers[seller["id"]] = seller
        return seller

    async def get_seller_by_user_id(self, user_id: str) -> Optional[dict]:
        for seller in self._sellers.values():
            if seller["user_id"] == user_id:
                return seller
        return None

    async def get_seller_by_id(self, seller_id: str) -> Optional[dict]:
        return self._sellers.get(seller_id)


class InventoryRepository:
    def __init__(self, collection: Any):
        self.collection = collection
        self._inventory: dict[str, dict] = {}

    async def create_inventory(self, product_id: str, quantity: int) -> dict:
        inventory = {
            "id": f"inv_{len(self._inventory) + 1}",
            "product_id": product_id,
            "quantity": quantity,
            "available_quantity": quantity,
            "reserved_quantity": 0,
        }
        self._inventory[inventory["id"]] = inventory
        return inventory

    async def get_inventory_by_product_id(self, product_id: str) -> Optional[dict]:
        for inv in self._inventory.values():
            if inv["product_id"] == product_id:
                return inv
        return None

    async def update_available_quantity(self, product_id: str, available_quantity: int) -> Optional[dict]:
        for inv in self._inventory.values():
            if inv["product_id"] == product_id:
                inv["available_quantity"] = available_quantity
                return inv
        return None
