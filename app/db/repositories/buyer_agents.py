from typing import Any, Optional, List
from bson import ObjectId
from typing import Any, Optional, List
from bson import ObjectId

class BuyerAgentRepository:
    def __init__(self, collection: Any):
        self.collection = collection

    async def create_agent(self, user_id: str, agent_dict: dict) -> dict:
        agent_dict["user_id"] = user_id
        agent_dict["status"] = "created"
        agent_dict["current_product_id"] = None
        agent_dict["current_seller_id"] = None
        agent_dict["events"] = [{
            "type": "agent_created",
            "description": "Buyer agent initialized and ready for execution."
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
            event = {"type": event_type, "description": description}
            result = await self.collection.update_one(
                {"_id": ObjectId(agent_id)},
                {"$push": {"events": event}}
            )
            return result.modified_count > 0
        except Exception:
            return False

# Aliases to satisfy any imports expecting split repository classes
BuyerTaskRepository = BuyerAgentRepository
BuyerAgentStateRepository = BuyerAgentRepository