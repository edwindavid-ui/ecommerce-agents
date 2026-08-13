from fastapi import APIRouter, HTTPException, status

from app.db.repositories.products import ProductRepository
from app.db.repositories.recommendations import RecommendationRepository
from app.db.repositories.sellers import SellerRepository, InventoryRepository
from app.schemas.product import ProductCreate
from app.schemas.recommendation import RecommendationRequest
from app.schemas.seller import SellerCreate, InventoryCreate
from app.services.recommendation_service import RecommendationService
from app.services.seller_service import SellerService, InventoryService

router = APIRouter(tags=["products", "sellers", "inventory", "recommendations"])

# Initialize repositories and services
# In a real app, these would come from dependency injection and use real MongoDB
product_repo = ProductRepository(collection=None)
seller_repo = SellerRepository(collection=None)
inventory_repo = InventoryRepository(collection=None)
rec_repo = RecommendationRepository(collection=None)

seller_service = SellerService(seller_repo)
inventory_service = InventoryService(inventory_repo)
recommendation_service = RecommendationService(product_repo, rec_repo)


@router.get("/products")
async def list_products(category: str = None, max_price: float = None):
    filters = product_repo.build_filters(category=category, max_price=max_price)
    return {"filters": filters, "results": []}


@router.post("/products", status_code=status.HTTP_201_CREATED)
async def create_product(payload: ProductCreate):
    # In a real implementation, we'd verify seller ownership via auth context
    return {
        "id": f"prod_{hash(payload.name) % 10000}",
        "name": payload.name,
        "category": payload.category,
        "price": payload.price,
        "seller_id": payload.seller_id,
        "status": payload.status,
    }


@router.post("/sellers/me", status_code=status.HTTP_201_CREATED)
async def create_seller_profile(payload: SellerCreate):
    # In real app, user_id comes from auth token
    user_id = "current_user"
    try:
        seller = await seller_service.create_seller(user_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return seller


@router.post("/inventory", status_code=status.HTTP_201_CREATED)
async def create_inventory(payload: InventoryCreate):
    try:
        inv = await inventory_service.create_inventory(payload.product_id, payload.quantity)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return inv


@router.post("/recommendations", status_code=status.HTTP_201_CREATED)
async def create_recommendation(payload: RecommendationRequest):
    try:
        result = await recommendation_service.generate_recommendations(payload.buyer_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return result


@router.get("/recommendations/{recommendation_id}")
async def get_recommendation(recommendation_id: str):
    try:
        result = await recommendation_service.get_recommendation(recommendation_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return result
