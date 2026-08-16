from typing import Any, Optional, List
from bson import ObjectId
from datetime import datetime, timezone

class OrderRepository:
    def __init__(self, collection: Any):
        self.collection = collection

    async def create_order(self, order_dict: dict) -> dict:
        # Generate a clean readable order reference number
        date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
        count = await self.collection.count_documents({})
        order_dict["order_number"] = f"ORD-{date_str}-{count + 1:04d}"
        
        now_str = datetime.now(timezone.utc).isoformat()
        order_dict["created_at"] = now_str
        order_dict["updated_at"] = now_str

        result = await self.collection.insert_one(order_dict)
        
        created = order_dict.copy()
        created["id"] = str(result.inserted_id)
        created.pop("_id", None)
        return created

    async def get_by_id(self, order_id: str) -> Optional[dict]:
        try:
            doc = await self.collection.find_one({"_id": ObjectId(order_id)})
            if doc:
                doc["id"] = str(doc["_id"])
                doc.pop("_id", None)
            return doc
        except Exception:
            return None

    async def get_by_buyer_id(self, buyer_id: str) -> List[dict]:
        cursor = self.collection.find({"buyer_id": buyer_id})
        docs = await cursor.to_list(length=100)
        orders = []
        for doc in docs:
            doc["id"] = str(doc["_id"])
            doc.pop("_id", None)
            orders.append(doc)
        return orders

    async def get_by_seller_id(self, seller_id: str) -> List[dict]:
        cursor = self.collection.find({"seller_id": seller_id})
        docs = await cursor.to_list(length=100)
        orders = []
        for doc in docs:
            doc["id"] = str(doc["_id"])
            doc.pop("_id", None)
            orders.append(doc)
        return orders

    async def update_status(self, order_id: str, new_status: str) -> Optional[dict]:
        try:
            now_str = datetime.now(timezone.utc).isoformat()
            doc = await self.collection.find_one_and_update(
                {"_id": ObjectId(order_id)},
                {"$set": {"status": new_status, "updated_at": now_str}},
                return_document=True
            )
            if doc:
                doc["id"] = str(doc["_id"])
                doc.pop("_id", None)
            return doc
        except Exception:
            return None