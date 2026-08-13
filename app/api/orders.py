from fastapi import APIRouter, HTTPException, Query, status

from app.db.repositories import negotiation_repo, order_repo
from app.schemas.order import OrderCreate, OrderStatusUpdate
from app.services.negotiation_service import NegotiationService
from app.services.order_service import OrderService

router = APIRouter(prefix="/orders", tags=["orders"])

# Initialize services with shared repositories
negotiation_service = NegotiationService(negotiation_repo, None)
order_service = OrderService(order_repo, negotiation_repo)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_order(payload: OrderCreate):
    """Create an order from an accepted negotiation."""
    try:
        result = await order_service.create_order_from_negotiation(payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return result


@router.get("/{order_id}")
async def get_order(order_id: str):
    """Retrieve an order by ID."""
    try:
        result = await order_service.get_order(order_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return result


@router.patch("/{order_id}/status")
async def update_order_status(order_id: str, payload: OrderStatusUpdate):
    """Update the status of an order."""
    try:
        result = await order_service.update_order_status(order_id, payload.status)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return result


@router.get("")
async def list_orders(
    buyer_id: str = Query(None),
    seller_id: str = Query(None),
):
    """List orders, optionally filtered by buyer_id or seller_id."""
    if buyer_id:
        orders = await order_service.list_orders_by_buyer(buyer_id)
        return {"buyer_id": buyer_id, "orders": orders}
    elif seller_id:
        orders = await order_service.list_orders_by_seller(seller_id)
        return {"seller_id": seller_id, "orders": orders}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must provide either buyer_id or seller_id",
        )
