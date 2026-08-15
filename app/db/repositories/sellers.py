from typing import Any, Optional

from app.schemas.seller import SellerCreate


class SellerRepository:
    def __init__(self, collection: Any):
        # We only need the MongoDB collection pointer here now
        self.collection = collection

    async def create_seller(self, user_id: str, seller_data: SellerCreate) -> dict:
        seller_dict = seller_data.model_dump()        
        seller_dict["user_id"] = user_id
        seller_dict["rating"] = 0.0
        seller_dict["status"] = "active"
        result = await self.collection.insert_one(seller_dict)
        seller_dict["id"] = str(result.inserted_id)
        
        return seller_dict

    async def get_seller_by_user_id(self, user_id: str) -> dict | None:
        seller = await self.collection.find_one({"user_id": user_id})
        
        if seller:
            seller["id"] = str(seller["_id"])
            
        return seller


class InventoryRepository:
    def __init__(self, collection: Any):
        self.collection = collection

    async def create_inventory(self, product_id: str, quantity: int) -> dict:
        inventory_dict = {
            "product_id": product_id,
            "quantity": quantity,
            "available_quantity": quantity,
            "reserved_quantity": 0,
        }
        
        # 1. Insert into MongoDB collection
        result = await self.collection.insert_one(inventory_dict)
        
        # 2. Format response and convert ObjectId to string id
        created_inventory = inventory_dict.copy()
        created_inventory["id"] = str(result.inserted_id)
        created_inventory.pop("_id", None)
        
        return created_inventory

    async def get_inventory_by_product_id(self, product_id: str) -> Optional[dict]:
        # 3. Query MongoDB for the inventory item
        doc = await self.collection.find_one({"product_id": product_id})
        if doc:
            doc["id"] = str(doc["_id"])
            doc.pop("_id", None)
        return doc

    async def update_available_quantity(self, product_id: str, available_quantity: int) -> Optional[dict]:
        # 4. Update MongoDB and return the updated document
        doc = await self.collection.find_one_and_update(
            {"product_id": product_id},
            {"$set": {"available_quantity": available_quantity}},
            return_document=True
        )
        if doc:
            doc["id"] = str(doc["_id"])
            doc.pop("_id", None)
        return doc