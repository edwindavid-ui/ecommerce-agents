from app.db.repositories.products import ProductRepository
from app.db.repositories.recommendations import RecommendationRepository
import uuid
from app.schemas.recommendation import RecommendationRequest, RecommendationResponse, RecommendationItem

class RecommendationService:
    def __init__(self, product_repo, inventory_repo, recommendation_repo, ai_service):
        self.product_repo = product_repo
        self.inventory_repo = inventory_repo
        self.recommendation_repo = recommendation_repo
        self.ai_service = ai_service

    async def recommend(self, request: RecommendationRequest, buyer_id: str = "anonymous_buyer") -> RecommendationResponse:
        # Stage 1: Hard filtering via Product Repository
        raw_products = await self.product_repo.search_products(
            query_str=request.query,
            category=request.category,
            min_price=request.min_price,
            max_price=request.max_price
        )

        request_id = str(uuid.uuid4())

        if not raw_products:
            response = RecommendationResponse(request_id=request_id, results=[])
            await self.recommendation_repo.create_recommendation(buyer_id, request, [])
            return response

        # Stage 2: Inventory Availability Filtering
        valid_candidates = []
        for product in raw_products:
            product_id = product["id"]
            seller_id = product["seller_id"]
            
            inv = await self.inventory_repo.get_inventory_by_seller_and_product(seller_id, product_id)
            
            if inv and inv.get("available_quantity", 0) > 0:
                product["available_quantity"] = inv["available_quantity"]
                valid_candidates.append(product)

        if not valid_candidates:
            response = RecommendationResponse(request_id=request_id, results=[])
            await self.recommendation_repo.create_recommendation(buyer_id, request, [])
            return response

        # Stage 3: AI Soft-Ranking using Gemini
        ranking_prompt = f"""
        You are an expert e-commerce recommendation system. 
        Analyze the user's request and preferences, then rank the provided in-stock product candidates.
        
        User Query: {request.query or "General recommendation"}
        User Preferences: {request.preferences}
        
        Candidates:
        {valid_candidates}
        
        Return a valid JSON object with a single key "rankings" containing a list of objects. Each object must include:
        - "product_id": (string matching the candidate's id)
        - "score": (float between 0.0 and 1.0 indicating fit)
        - "reason": (string explaining why it fits based on user preferences)
        """

        ai_response = self.ai_service.provider.call_model(ranking_prompt)
        rankings = ai_response.get("rankings", [])

        results = []
        ranking_map = {r["product_id"]: r for r in rankings}

        for product in valid_candidates:
            p_id = product["id"]
            ai_data = ranking_map.get(p_id, {"score": 0.5, "reason": "Matches basic catalog criteria."})
            
            results.append(RecommendationItem(
                product_id=p_id,
                seller_id=product["seller_id"],
                score=float(ai_data.get("score", 0.5)),
                reason=ai_data.get("reason", "Meets search requirements."),
                product=product
            ))

        results.sort(key=lambda x: x.score, reverse=True)
        limited_results = results[:request.limit]

        # Save recommendation history to MongoDB
        await self.recommendation_repo.create_recommendation(
            buyer_id=buyer_id,
            request=request,
            results=limited_results
        )

        return RecommendationResponse(
            request_id=request_id,
            results=limited_results
        )