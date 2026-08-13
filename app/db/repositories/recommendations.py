from typing import Any, Optional

from app.schemas.recommendation import RecommendationRequest, RecommendationResult


class RecommendationRepository:
    def __init__(self, collection: Any):
        self.collection = collection
        self._recommendations: dict[str, dict] = {}

    async def create_recommendation(self, buyer_id: str, request: RecommendationRequest, results: list[RecommendationResult]) -> dict:
        rec_id = f"rec_{len(self._recommendations) + 1}"
        rec = {
            "id": rec_id,
            "buyer_id": buyer_id,
            "status": "completed",
            "results": [r.model_dump() for r in results],
            "filters_applied": {
                "category": request.category,
                "max_price": request.max_price,
                "min_price": request.min_price,
            },
        }
        self._recommendations[rec_id] = rec
        return rec

    async def get_recommendation_by_id(self, recommendation_id: str) -> Optional[dict]:
        return self._recommendations.get(recommendation_id)

    async def list_recommendations_by_buyer(self, buyer_id: str) -> list[dict]:
        return [r for r in self._recommendations.values() if r["buyer_id"] == buyer_id]
