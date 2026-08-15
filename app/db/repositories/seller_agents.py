from typing import Any, Optional
from app.schemas.seller_agent import SellerAgentCreate
from bson import ObjectId

class SellerAgentRepository:
    def __init__(self, collection: Any):
        self.collection = collection

    async def create_agent(self, agent_data: Any) -> dict:
        agent_dict = agent_data.model_dump() if hasattr(agent_data, "model_dump") else dict(agent_data)
        agent_dict["current_round"] = 0
        agent_dict["status"] = "active"
        
        result = await self.collection.insert_one(agent_dict)
        
        created_agent = agent_dict.copy()
        created_agent["id"] = str(result.inserted_id)
        created_agent.pop("_id", None)
        
        return created_agent

    async def get_agent_by_id(self, agent_id: str) -> Optional[dict]:
        try:
            doc = await self.collection.find_one({"_id": ObjectId(agent_id)})
            if doc:
                doc["id"] = str(doc["_id"])
                doc.pop("_id", None)
            return doc
        except Exception:
            return None

    async def get_agent_by_seller_and_product(self, seller_id: str, product_id: str) -> Optional[dict]:
        doc = await self.collection.find_one({"seller_id": seller_id, "product_id": product_id})
        if doc:
            doc["id"] = str(doc["_id"])
            doc.pop("_id", None)
        return doc

    async def list_agents_by_seller(self, seller_id: str) -> list[dict]:
        cursor = self.collection.find({"seller_id": seller_id})
        raw_docs = await cursor.to_list(length=100)
        
        docs = []
        for doc in raw_docs:
            doc["id"] = str(doc["_id"])
            doc.pop("_id", None)
            docs.append(doc)
        return docs

    async def update_agent_round(self, agent_id: str, round_num: int) -> Optional[dict]:
        try:
            doc = await self.collection.find_one_and_update(
                {"_id": ObjectId(agent_id)},
                {"$set": {"current_round": round_num}},
                return_document=True
            )
            if doc:
                doc["id"] = str(doc["_id"])
                doc.pop("_id", None)
            return doc
        except Exception:
            return None

    async def update_agent_status(self, agent_id: str, status: str) -> Optional[dict]:
        try:
            doc = await self.collection.find_one_and_update(
                {"_id": ObjectId(agent_id)},
                {"$set": {"status": status}},
                return_document=True
            )
            if doc:
                doc["id"] = str(doc["_id"])
                doc.pop("_id", None)
            return doc
        except Exception:
            return None