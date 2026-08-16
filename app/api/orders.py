from fastapi import APIRouter, HTTPException, status, Depends
from app.auth.deps import get_current_user_id
from app.db.mongodb import database
from app.db.repositories.orders import OrderRepository
from app.db.repositories.negotiations import NegotiationRepository
from app.db.repositories.products import ProductRepository
from app.db.repositories.sellers import InventoryRepository
from app.services.order_service import OrderService
from app.schemas.order import OrderCreate, OrderStatusUpdate, OrderResponse

router = APIRouter(prefix="/orders", tags=["orders"])

order_repo = OrderRepository(collection=database.get_collection("orders"))
negotiation_repo = NegotiationRepository(collection=database.get_collection("negotiations"))
product_repo = ProductRepository(collection=database.get_collection("products"))
inventory_repo = InventoryRepository(collection=database.get_collection("inventory"))

order_service = OrderService(
    order_repo=order_repo,
    negotiation_repo=negotiation_repo,
    product_repo=product_repo,
    inventory_repo=inventory_repo
)

@router.post("", status_code=status.HTTP_201_CREATED, response_model=OrderResponse)
async def create_order_from_negotiation(
    payload: OrderCreate,
    current_user_id: str = Depends(get_current_user_id)
):
    """Securely create an order from an accepted negotiation and deduct inventory atomically."""
    try:
        order = await order_service.create_from_negotiation(payload.negotiation_id)
        return order
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))

@router.get("/{order_id}", status_code=status.HTTP_200_OK, response_model=OrderResponse)
async def get_order(order_id: str):
    """Retrieve details for a specific order."""
    order = await order_repo.get_by_id(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.get("/user/me", status_code=status.HTTP_200_OK)
async def list_my_buyer_orders(current_user_id: str = Depends(get_current_user_id)):
    """List all orders belonging to the authenticated buyer."""
    orders = await order_repo.get_by_buyer_id(current_user_id)
    return {"results": orders}

@router.patch("/{order_id}/status", status_code=status.HTTP_200_OK, response_model=OrderResponse)
async def update_order_status(
    order_id: str,
    payload: OrderStatusUpdate,
    current_user_id: str = Depends(get_current_user_id)
):
    """Update the status of an order."""
    updated = await order_repo.update_status(order_id, payload.status)
    if not updated:
        raise HTTPException(status_code=404, detail="Order not found")
    return updated