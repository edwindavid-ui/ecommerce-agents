from fastapi import APIRouter, HTTPException, status, Depends
from app.auth.deps import get_current_user_id
from app.db.mongodb import database
from typing import Optional, Any
from app.db.repositories.products import ProductRepository
from app.db.repositories.recommendations import RecommendationRepository
from app.db.repositories.sellers import SellerRepository, InventoryRepository
from app.schemas.product import ProductCreate, ProductUpdate
from app.schemas.recommendation import RecommendationRequest, RecommendationResponse
from app.schemas.seller import (
    SellerCreate, 
    InventoryCreate, 
    InventoryUpdate, 
    InventoryReservation, 
    InventoryRelease, 
    SellerUpdate
)
from app.services.recommendation_service import RecommendationService
from app.services.seller_service import SellerService, InventoryService
from app.services.ai_service import AIService


router = APIRouter(tags=["products", "sellers", "inventory", "recommendations"])

product_repo = ProductRepository(collection=database.get_collection("products"))
seller_repo = SellerRepository(collection=database.get_collection("sellers"))
inventory_repo = InventoryRepository(collection=database.get_collection("inventory"))
rec_repo = RecommendationRepository(collection=database.get_collection("recommendations"))

seller_service = SellerService(seller_repo)
inventory_service = InventoryService(inventory_repo)
ai_service = AIService()

# Pass all four required dependencies
recommendation_service = RecommendationService(
    product_repo=product_repo,
    inventory_repo=inventory_repo,
    recommendation_repo=rec_repo,
    ai_service=ai_service
)

# --- Products API ---

@router.post("/products", status_code=status.HTTP_201_CREATED)
async def create_product(payload: ProductCreate):
    product_dict = payload.model_dump()
    created_product = await product_repo.create_product(product_dict)
    return {
        "message": "Product created successfully",
        "product": created_product
    }

@router.get("/products")
async def list_products(
    category: Optional[str] = None,
    max_price: Optional[float] = None
):
    products = await product_repo.get_products(category=category, max_price=max_price)
    return {
        "filters": {
            "category": category,
            "max_price": max_price
        },
        "results": products
    }

@router.get("/products/search")
async def search_products(
    query: Optional[str] = None,
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None
):
    products = await product_repo.search_products(
        query_str=query,
        category=category,
        min_price=min_price,
        max_price=max_price
    )
    return {
        "query": query,
        "results": products
    }

@router.get("/products/{product_id}")
async def get_product(product_id: str):
    product = await product_repo.get_product(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"product": product}

@router.put("/products/{product_id}")
async def update_product(product_id: str, payload: ProductUpdate):
    update_data = payload.model_dump(exclude_unset=True)
    product = await product_repo.update_product(product_id, update_data)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return {
        "message": "Product updated successfully",
        "product": product
    }

@router.delete("/products/{product_id}")
async def deactivate_product(product_id: str):
    success = await product_repo.deactivate_product(product_id)
    if not success:
        raise HTTPException(status_code=404, detail="Product not found or already inactive")
    return {"message": "Product deactivated successfully"}


# --- Sellers API (Secured with JWT) ---

@router.post("/sellers/me", status_code=status.HTTP_201_CREATED)
async def create_seller_profile(
    payload: SellerCreate, 
    current_user_id: str = Depends(get_current_user_id)
):
    existing = await seller_repo.get_seller_by_user_id(current_user_id)
    if existing:
        raise HTTPException(status_code=400, detail="Seller profile already exists for this user")
    
    seller_dict = payload.model_dump()
    created = await seller_repo.create_seller(current_user_id, seller_dict)
    return {
        "message": "Seller profile created successfully",
        "seller": created
    }

@router.get("/sellers/me")
async def get_my_seller_profile(
    current_user_id: str = Depends(get_current_user_id)
):
    seller = await seller_repo.get_seller_by_user_id(current_user_id)
    if not seller:
        raise HTTPException(status_code=404, detail="Seller profile not found")
    return {"seller": seller}

@router.put("/sellers/me")
async def update_my_seller_profile(
    payload: SellerUpdate, 
    current_user_id: str = Depends(get_current_user_id)
):
    seller = await seller_repo.get_seller_by_user_id(current_user_id)
    if not seller:
        raise HTTPException(status_code=404, detail="Seller profile not found")
    
    update_data = payload.model_dump(exclude_unset=True)
    updated = await seller_repo.update_seller(seller["id"], update_data)
    return {
        "message": "Seller profile updated successfully",
        "seller": updated
    }

@router.get("/sellers")
async def list_sellers(status_filter: Optional[str] = None):
    sellers = await seller_repo.get_sellers(status=status_filter)
    return {"results": sellers}

@router.get("/sellers/{seller_id}")
async def get_seller(seller_id: str):
    seller = await seller_repo.get_seller_by_id(seller_id)
    if not seller:
        raise HTTPException(status_code=404, detail="Seller not found")
    return {"seller": seller}

@router.get("/sellers/{seller_id}/products")
async def get_seller_products(seller_id: str):
    products = await product_repo.get_products_by_seller(seller_id)
    return {
        "seller_id": seller_id,
        "products": products
    }

@router.get("/sellers/{seller_id}/inventory")
async def get_seller_inventory(seller_id: str):
    cursor = inventory_repo.collection.find({"seller_id": seller_id})
    raw_docs = await cursor.to_list(length=100)
    inventory = []
    for doc in raw_docs:
        doc["id"] = str(doc["_id"])
        doc.pop("_id", None)
        inventory.append(doc)
    return {
        "seller_id": seller_id,
        "inventory": inventory
    }


# --- Inventory API ---

@router.post("/inventory", status_code=status.HTTP_201_CREATED)
async def create_inventory(payload: InventoryCreate):
    try:
        inv = await inventory_service.create_inventory(
            payload.product_id, payload.seller_id, payload.quantity
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return inv

@router.get("/inventory/{inventory_id}")
async def get_inventory(inventory_id: str):
    try:
        inv = await inventory_service.get_inventory(inventory_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    return inv

@router.patch("/inventory/{inventory_id}")
async def update_inventory(inventory_id: str, payload: InventoryUpdate):
    try:
        inv = await inventory_service.update_inventory(inventory_id, payload.quantity)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return inv

@router.post("/inventory/{inventory_id}/reserve", status_code=status.HTTP_200_OK)
async def reserve_inventory(inventory_id: str, payload: InventoryReservation):
    try:
        inv = await inventory_service.reserve_stock(inventory_id, payload.quantity)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return inv

@router.post("/inventory/{inventory_id}/release", status_code=status.HTTP_200_OK)
async def release_inventory(inventory_id: str, payload: InventoryRelease):
    try:
        inv = await inventory_service.release_stock(inventory_id, payload.quantity)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return inv


# --- Recommendations API ---

@router.post("/recommendations", status_code=status.HTTP_200_OK, response_model=RecommendationResponse)
async def generate_recommendations(payload: RecommendationRequest):
    try:
        response = await recommendation_service.recommend(payload)
        return response
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Recommendation pipeline failed: {str(exc)}")
