from app.db.repositories.products import ProductRepository
from app.db.repositories.recommendations import RecommendationRepository
from app.schemas.recommendation import RecommendationRequest, RecommendationResult

class RecommendationService:
    def __init__(self, product_repo, rec_repo):
        self.product_repo = product_repo
        self.rec_repo = rec_repo

    async def generate_recommendations(self, buyer_id: str, request) -> dict:
        # Real MVP Standard: Query actual products from MongoDB using filters
        db_products = await self.product_repo.list_products(
            category=request.category,
            max_price=request.max_price
        )
        
        results = []
        for p in db_products:
            results.append(
                RecommendationResult(
                    product_id=p.get("id"),
                    name=p.get("name"),
                    category=p.get("category", "general"),
                    price=p.get("price", 0.0),
                    seller_id=p.get("seller_id", "unknown"),
                    score=0.95
                )
            )
        
        rec = await self.rec_repo.create_recommendation(buyer_id, request, results)
        
        return {
            "recommendation_id": rec["id"],
            "buyer_id": rec["buyer_id"],
            "status": rec["status"],
            "results": rec["results"],
            "filters_applied": rec["filters_applied"]
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
            "filters_applied": rec["filters_applied"]
        }