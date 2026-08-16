from typing import Any, Optional, List
from bson import ObjectId
from app.schemas.recommendation import RecommendationRequest, RecommendationResponse, RecommendationItem

class RecommendationRepository:
    def __init__(self, collection: Any):
        self.collection = collection

    async def create_recommendation(self, buyer_id: str, request: Any, results: list) -> dict:
        rec_dict = {
            "buyer_id": buyer_id,
            "status": "completed",
            "results": [r.model_dump() for r in results],
            "filters_applied": {
                "category": request.category,
                "max_price": request.max_price,
                "min_price": request.min_price if hasattr(request, "min_price") else None,
            }
        }
        
        result = await self.collection.insert_one(rec_dict)
        
        created_rec = rec_dict.copy()
        created_rec["id"] = str(result.inserted_id)
        created_rec.pop("_id", None)
        
        return created_rec

    async def get_recommendation_by_id(self, recommendation_id: str) -> Optional[dict]:
        try:
            doc = await self.collection.find_one({"_id": ObjectId(recommendation_id)})
            if doc:
                doc["id"] = str(doc["_id"])
                doc.pop("_id", None)
            return doc
        except Exception:
            return None

    async def list_recommendations_by_buyer(self, buyer_id: str) -> List[dict]:
        cursor = self.collection.find({"buyer_id": buyer_id})
        raw_docs = await cursor.to_list(length=100)
        
        docs = []
        for doc in raw_docs:
            doc["id"] = str(doc["_id"])
            doc.pop("_id", None)
            docs.append(doc)
        return docs