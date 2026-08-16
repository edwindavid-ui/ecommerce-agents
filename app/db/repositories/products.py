from typing import Any, Optional, List
from bson import ObjectId

class ProductRepository:
    def __init__(self, collection: Any):
        self.collection = collection

    async def create_product(self, product_dict: dict) -> dict:
        product_dict["active"] = product_dict.get("active", True)
        result = await self.collection.insert_one(product_dict)
        
        created = product_dict.copy()
        created["id"] = str(result.inserted_id)
        created.pop("_id", None)
        return created

    async def get_products(self, category: Optional[str] = None, max_price: Optional[float] = None) -> List[dict]:
        query = {"active": True}
        if category:
            query["category"] = category
        if max_price is not None:
            query["price"] = {"$lte": max_price}

        cursor = self.collection.find(query)
        raw_docs = await cursor.to_list(length=100)
        
        products = []
        for doc in raw_docs:
            doc["id"] = str(doc["_id"])
            doc.pop("_id", None)
            products.append(doc)
        return products

    async def get_product(self, product_id: str) -> Optional[dict]:
        try:
            object_id = ObjectId(product_id)
        except Exception:
            return None

        doc = await self.collection.find_one({"_id": object_id})
        if doc:
            doc["id"] = str(doc["_id"])
            doc.pop("_id", None)
        return doc

    async def update_product(self, product_id: str, update_data: dict) -> Optional[dict]:
        try:
            object_id = ObjectId(product_id)
        except Exception:
            return None

        doc = await self.collection.find_one_and_update(
            {"_id": object_id},
            {"$set": update_data},
            return_document=True
        )
        if doc:
            doc["id"] = str(doc["_id"])
            doc.pop("_id", None)
        return doc

    async def deactivate_product(self, product_id: str) -> bool:
        try:
            object_id = ObjectId(product_id)
        except Exception:
            return False

        result = await self.collection.update_one(
            {"_id": object_id},
            {"$set": {"active": False}}
        )
        return result.modified_count > 0

    async def search_products(
        self, 
        query_str: Optional[str] = None, 
        category: Optional[str] = None, 
        min_price: Optional[float] = None, 
        max_price: Optional[float] = None
    ) -> List[dict]:
        query = {"active": True}
        
        if category:
            query["category"] = category
            
        price_filter = {}
        if min_price is not None:
            price_filter["$gte"] = min_price
        if max_price is not None:
            price_filter["$lte"] = max_price
        if price_filter:
            query["price"] = price_filter

        if query_str:
            # Basic text search on name or description
            query["$or"] = [
                {"name": {"$regex": query_str, "$options": "i"}},
                {"description": {"$regex": query_str, "$options": "i"}}
            ]

        cursor = self.collection.find(query)
        raw_docs = await cursor.to_list(length=100)
        
        products = []
        for doc in raw_docs:
            doc["id"] = str(doc["_id"])
            doc.pop("_id", None)
            products.append(doc)
        return products

    async def get_products_by_seller(self, seller_id: str) -> List[dict]:
        cursor = self.collection.find({"seller_id": seller_id, "active": True})
        raw_docs = await cursor.to_list(length=100)
        
        products = []
        for doc in raw_docs:
            doc["id"] = str(doc["_id"])
            doc.pop("_id", None)
            products.append(doc)
        return products