from typing import Any, Optional

from app.schemas.seller import SellerCreate


class SellerRepository:
    def __init__(self, collection: Any):
        # We only need the MongoDB collection pointer here now
        self.collection = collection

    async def create_seller(self, user_id: str, seller_data: SellerCreate) -> dict:
        # 1. Convert the Pydantic model to a standard dictionary
        seller_dict = seller_data.model_dump()
        
        # 2. Add the extra required fields
        seller_dict["user_id"] = user_id
        seller_dict["rating"] = 0.0
        seller_dict["status"] = "active"
        
        # 3. Actually insert the document into MongoDB!
        result = await self.collection.insert_one(seller_dict)
        
        # 4. Attach the generated MongoDB ObjectId (as a string) before returning
        seller_dict["id"] = str(result.inserted_id)
        
        return seller_dict

    async def get_seller_by_user_id(self, user_id: str) -> dict | None:
        # You will also need to update this method to query the real database!
        seller = await self.collection.find_one({"user_id": user_id})
        
        if seller:
            # Convert the raw _id to a string id for your response schema
            seller["id"] = str(seller["_id"])
            
        return seller

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
