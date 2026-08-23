from typing import Any, Optional, List
from bson import ObjectId
from datetime import datetime, timezone

class SellerAgentRepository:
    def __init__(self, collection: Any):
        self.collection = collection

    async def create_agent(self, seller_id: str, agent_dict: dict) -> dict:
        agent_dict["seller_id"] = seller_id
        agent_dict["status"] = "idle"
        agent_dict["active_negotiations"] = 0
        agent_dict["events"] = [{
            "type": "agent_created",
            "description": "Seller agent initialized and standing by.",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }]
        
        result = await self.collection.insert_one(agent_dict)
        
        created = agent_dict.copy()
        created["id"] = str(result.inserted_id)
        created.pop("_id", None)
        return created

    async def get_agent(self, agent_id: str) -> Optional[dict]:
        try:
            doc = await self.collection.find_one({"_id": ObjectId(agent_id)})
            if doc:
                doc["id"] = str(doc["_id"])
                doc.pop("_id", None)
            return doc
        except Exception:
            return None

    async def get_agents_by_seller_id(self, seller_id: str) -> List[dict]:
        try:
            cursor = self.collection.find({"seller_id": seller_id})
            docs = await cursor.to_list(length=100)
            agents = []
            for doc in docs:
                doc["id"] = str(doc["_id"])
                doc.pop("_id", None)
                agents.append(doc)
            return agents
        except Exception:
            return []

    async def update_status(self, agent_id: str, status: str, extra_updates: Optional[dict] = None) -> Optional[dict]:
        try:
            update_data = {"status": status}
            if extra_updates:
                update_data.update(extra_updates)
                
            doc = await self.collection.find_one_and_update(
                {"_id": ObjectId(agent_id)},
                {"$set": update_data},
                return_document=True
            )
            if doc:
                doc["id"] = str(doc["_id"])
                doc.pop("_id", None)
            return doc
        except Exception:
            return None

    async def add_event(self, agent_id: str, event_type: str, description: str) -> bool:
        try:
            event = {
                "type": event_type, 
                "description": description,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            result = await self.collection.update_one(
                {"_id": ObjectId(agent_id)},
                {"$push": {"events": event}}
            )
            return result.modified_count > 0
        except Exception:
            return False
