from typing import Any, Optional, List
from bson import ObjectId
from datetime import datetime, timezone

class NegotiationRepository:
    def __init__(self, collection: Any):
        self.collection = collection

    async def create(self, neg_dict: dict) -> dict:
        neg_dict["status"] = "active"
        neg_dict["current_turn"] = "seller"  # Buyer makes the initial offer, so it's the seller's turn
        neg_dict["round"] = 1
        neg_dict["final_price"] = None
        
        # Initialize the audit log with the opening bid
        neg_dict["offers"] = [{
            "round": 1,
            "party": "buyer",
            "price": neg_dict["initial_offer"],
            "message": "Initial offer from buyer",
            "created_at": datetime.now(timezone.utc).isoformat()
        }]
        neg_dict["created_at"] = datetime.now(timezone.utc).isoformat()
        neg_dict["updated_at"] = neg_dict["created_at"]
        
        result = await self.collection.insert_one(neg_dict)
        
        created = neg_dict.copy()
        created["id"] = str(result.inserted_id)
        created.pop("_id", None)
        return created

    async def get_by_id(self, neg_id: str) -> Optional[dict]:
        try:
            doc = await self.collection.find_one({"_id": ObjectId(neg_id)})
            if doc:
                doc["id"] = str(doc["_id"])
                doc.pop("_id", None)
            return doc
        except Exception:
            return None

    async def add_offer(self, neg_id: str, party: str, price: float, message: Optional[str], new_round: int, next_turn: str) -> Optional[dict]:
        try:
            offer = {
                "round": new_round,
                "party": party,
                "price": price,
                "message": message,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            
            doc = await self.collection.find_one_and_update(
                {"_id": ObjectId(neg_id)},
                {
                    "$push": {"offers": offer},
                    "$set": {
                        "current_offer": price,
                        "round": new_round,
                        "current_turn": next_turn,
                        "updated_at": datetime.now(timezone.utc).isoformat()
                    }
                },
                return_document=True
            )
            if doc:
                doc["id"] = str(doc["_id"])
                doc.pop("_id", None)
            return doc
        except Exception:
            return None

    async def update_status(self, neg_id: str, status: str, final_price: Optional[float] = None) -> Optional[dict]:
        try:
            update_fields = {
                "status": status,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            if final_price is not None:
                update_fields["final_price"] = final_price

            doc = await self.collection.find_one_and_update(
                {"_id": ObjectId(neg_id)},
                {"$set": update_fields},
                return_document=True
            )
            if doc:
                doc["id"] = str(doc["_id"])
                doc.pop("_id", None)
            return doc
        except Exception:
            return None
