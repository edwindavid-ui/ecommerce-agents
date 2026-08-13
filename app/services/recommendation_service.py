from app.db.repositories.products import ProductRepository
from app.db.repositories.recommendations import RecommendationRepository
from app.schemas.recommendation import RecommendationRequest, RecommendationResult


class RecommendationService:
    def __init__(self, product_repo: ProductRepository, rec_repo: RecommendationRepository):
        self.product_repo = product_repo
        self.rec_repo = rec_repo

    async def generate_recommendations(self, buyer_id: str, request: RecommendationRequest) -> dict:
        filters = self.product_repo.build_filters(
            category=request.category,
            max_price=request.max_price,
        )

        # MVP: Simple deterministic results based on filters
        # In real system, would query database and apply ranking
        results = [
            RecommendationResult(
                product_id="prod_1",
                name="Budget Laptop",
                category=request.category or "electronics",
                price=600.0,
                seller_id="seller_1",
                score=0.85,
            )
        ] if request.category else []

        rec = await self.rec_repo.create_recommendation(buyer_id, request, results)
        return {
            "recommendation_id": rec["id"],
            "buyer_id": rec["buyer_id"],
            "status": rec["status"],
            "results": rec["results"],
            "filters_applied": rec["filters_applied"],
        }

    async def get_recommendation(self, recommendation_id: str) -> dict:
        rec = await self.rec_repo.get_recommendation_by_id(recommendation_id)
        if not rec:
            raise ValueError("Recommendation not found")
        return {
            "recommendation_id": rec["id"],
            "buyer_id": rec["buyer_id"],
            "status": rec["status"],
            "results": rec["results"],
            "filters_applied": rec["filters_applied"],
        }
