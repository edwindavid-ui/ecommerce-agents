from fastapi import APIRouter, HTTPException, status, Depends
from app.auth.deps import get_current_user
from app.db.mongodb import database

from app.db.repositories.products import ProductRepository
from app.db.repositories.recommendations import RecommendationRepository
from app.db.repositories.sellers import SellerRepository, InventoryRepository
from app.schemas.product import ProductCreate
from app.schemas.recommendation import RecommendationRequest
from app.schemas.seller import SellerCreate, InventoryCreate
from app.services.recommendation_service import RecommendationService
from app.services.seller_service import SellerService, InventoryService

router = APIRouter(tags=["products", "sellers", "inventory", "recommendations"])

product_repo = ProductRepository(collection=database.get_collection("products"))
seller_repo = SellerRepository(collection=database.get_collection("sellers"))
inventory_repo = InventoryRepository(collection=database.get_collection("inventory"))
rec_repo = RecommendationRepository(collection=database.get_collection("recommendations"))

seller_service = SellerService(seller_repo)
inventory_service = InventoryService(inventory_repo)
recommendation_service = RecommendationService(product_repo, rec_repo)


@router.get("/products")
async def list_products(category: str = None, max_price: float = None):
    products = await product_repo.list_products(category=category, max_price=max_price)
    return {"results": products}

@router.post("/products", status_code=status.HTTP_201_CREATED)
async def create_product(payload: ProductCreate):
    product_dict = payload.model_dump()
    created_product = await product_repo.create_product(product_dict)
    return {
        "message": "Product created successfully",
        "product": created_product
    }


@router.post("/sellers/me", status_code=status.HTTP_201_CREATED)
async def create_seller_profile(payload: SellerCreate, current_user_id: str = Depends(get_current_user)):
    try:
        seller = await seller_service.create_seller(current_user_id, payload)
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
