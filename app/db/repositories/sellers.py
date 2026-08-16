from typing import Any, Optional, List
from bson import ObjectId

from app.schemas.seller import SellerCreate


class SellerRepository:
    def __init__(self, collection: Any):
        self.collection = collection

    async def create_seller(self, user_id: str, seller_dict: dict) -> dict:
        seller_dict["user_id"] = user_id
        # Default baseline negotiation bounds for the seller agent
        seller_dict["negotiation_config"] = {
            "negotiation_enabled": True,
            "min_discount_percent": 5.0,
            "max_discount_percent": 15.0
        }
        
        result = await self.collection.insert_one(seller_dict)
        
        created = seller_dict.copy()
        created["id"] = str(result.inserted_id)
        created.pop("_id", None)
        return created

    async def get_seller_by_id(self, seller_id: str) -> Optional[dict]:
        try:
            doc = await self.collection.find_one({"_id": ObjectId(seller_id)})
            if doc:
                doc["id"] = str(doc["_id"])
                doc.pop("_id", None)
            return doc
        except Exception:
            return None

    async def get_seller_by_user_id(self, user_id: str) -> Optional[dict]:
        doc = await self.collection.find_one({"user_id": user_id})
        if doc:
            doc["id"] = str(doc["_id"])
            doc.pop("_id", None)
        return doc

    async def get_sellers(self, status: Optional[str] = None) -> List[dict]:
        query = {}
        if status:
            query["status"] = status
            
        cursor = self.collection.find(query)
        raw_docs = await cursor.to_list(length=100)
        
        sellers = []
        for doc in raw_docs:
            doc["id"] = str(doc["_id"])
            doc.pop("_id", None)
            sellers.append(doc)
        return sellers

    async def update_seller(self, seller_id: str, update_data: dict) -> Optional[dict]:
        try:
            doc = await self.collection.find_one_and_update(
                {"_id": ObjectId(seller_id)},
                {"$set": update_data},
                return_document=True
            )
            if doc:
                doc["id"] = str(doc["_id"])
                doc.pop("_id", None)
            return doc
        except Exception:
            return None

    async def update_negotiation_config(self, seller_id: str, config_data: dict) -> Optional[dict]:
        try:
            doc = await self.collection.find_one_and_update(
                {"_id": ObjectId(seller_id)},
                {"$set": {"negotiation_config": config_data}},
                return_document=True
            )
            if doc:
                doc["id"] = str(doc["_id"])
                doc.pop("_id", None)
            return doc
        except Exception:
            return None

class InventoryRepository:
    def __init__(self, collection: Any):
        self.collection = collection

    async def create_inventory(self, product_id: str, seller_id: str, quantity: int) -> dict:
        inventory_dict = {
            "product_id": product_id,
            "seller_id": seller_id,
            "quantity": quantity,
            "available_quantity": quantity,
            "reserved_quantity": 0,
        }
        
        result = await self.collection.insert_one(inventory_dict)
        
        created_inventory = inventory_dict.copy()
        created_inventory["id"] = str(result.inserted_id)
        created_inventory.pop("_id", None)
        
        return created_inventory

    async def get_inventory_by_id(self, inventory_id: str) -> Optional[dict]:
        try:
            doc = await self.collection.find_one({"_id": ObjectId(inventory_id)})
            if doc:
                doc["id"] = str(doc["_id"])
                doc.pop("_id", None)
            return doc
        except Exception:
            return None

    async def get_inventory_by_seller_and_product(self, seller_id: str, product_id: str) -> Optional[dict]:
        doc = await self.collection.find_one({"seller_id": seller_id, "product_id": product_id})
        if doc:
            doc["id"] = str(doc["_id"])
            doc.pop("_id", None)
        return doc

    async def update_quantity(self, inventory_id: str, new_quantity: int) -> Optional[dict]:
        try:
            doc = await self.collection.find_one({"_id": ObjectId(inventory_id)})
            if not doc:
                return None
            
            reserved = doc.get("reserved_quantity", 0)
            if new_quantity < reserved:
                raise ValueError("New total quantity cannot be less than currently reserved quantity")
            
            available = new_quantity - reserved
            updated_doc = await self.collection.find_one_and_update(
                {"_id": ObjectId(inventory_id)},
                {"$set": {"quantity": new_quantity, "available_quantity": available}},
                return_document=True
            )
            if updated_doc:
                updated_doc["id"] = str(updated_doc["_id"])
                updated_doc.pop("_id", None)
            return updated_doc
        except Exception as e:
            raise e

    async def reserve_inventory(self, inventory_id: str, amount: int) -> Optional[dict]:
        try:
            # Atomically verifies availability and shifts count to reserved
            doc = await self.collection.find_one_and_update(
                {"_id": ObjectId(inventory_id), "available_quantity": {"$gte": amount}},
                {"$inc": {"available_quantity": -amount, "reserved_quantity": amount}},
                return_document=True
            )
            if doc:
                doc["id"] = str(doc["_id"])
                doc.pop("_id", None)
            return doc
        except Exception:
            return None

    async def release_inventory(self, inventory_id: str, amount: int) -> Optional[dict]:
        try:
            # Atomically shifts count back from reserved to available
            doc = await self.collection.find_one_and_update(
                {"_id": ObjectId(inventory_id), "reserved_quantity": {"$gte": amount}},
                {"$inc": {"available_quantity": amount, "reserved_quantity": -amount}},
                return_document=True
            )
            if doc:
                doc["id"] = str(doc["_id"])
                doc.pop("_id", None)
            return doc
        except Exception:
            return None