from app.db.repositories.orders import OrderRepository
from app.db.repositories.negotiations import NegotiationRepository
from app.schemas.order import OrderCreate


class OrderService:
    def __init__(self, order_repo: OrderRepository, negotiation_repo: NegotiationRepository):
        self.order_repo = order_repo
        self.negotiation_repo = negotiation_repo

    async def create_order_from_negotiation(self, order_data: OrderCreate) -> dict:
        """Create an order from an accepted negotiation."""
        # Validate negotiation exists and is accepted
        negotiation = await self.negotiation_repo.get_negotiation_by_id(order_data.negotiation_id)
        if not negotiation:
            raise ValueError("Negotiation not found")
        
        if negotiation["status"] != "accepted":
            raise ValueError(f"Cannot create order from negotiation with status: {negotiation['status']}")
        
        if negotiation["final_price"] is None:
            raise ValueError("Negotiation does not have a final price")
        
        # Create order
        order = await self.order_repo.create_order(order_data, negotiation)
        
        return {
            "order_id": order["id"],
            "negotiation_id": order["negotiation_id"],
            "buyer_id": order["buyer_id"],
            "seller_id": order["seller_id"],
            "product_id": order["product_id"],
            "final_price": order["final_price"],
            "status": order["status"],
            "created_at": order["created_at"],
            "updated_at": order["updated_at"],
        }

    async def get_order(self, order_id: str) -> dict:
        """Retrieve an order by ID."""
        order = await self.order_repo.get_order_by_id(order_id)
        if not order:
            raise ValueError("Order not found")
        
        return {
            "order_id": order["id"],
            "negotiation_id": order["negotiation_id"],
            "buyer_id": order["buyer_id"],
            "seller_id": order["seller_id"],
            "product_id": order["product_id"],
            "final_price": order["final_price"],
            "status": order["status"],
            "created_at": order["created_at"],
            "updated_at": order["updated_at"],
        }

    async def update_order_status(self, order_id: str, status: str) -> dict:
        """Update the status of an order."""
        # Validate status
        valid_statuses = ["pending", "confirmed", "processing", "delivered", "cancelled"]
        if status not in valid_statuses:
            raise ValueError(f"Invalid status: {status}")
        
        order = await self.order_repo.update_order_status(order_id, status)
        if not order:
            raise ValueError("Order not found")
        
        return {
            "order_id": order["id"],
            "negotiation_id": order["negotiation_id"],
            "buyer_id": order["buyer_id"],
            "seller_id": order["seller_id"],
            "product_id": order["product_id"],
            "final_price": order["final_price"],
            "status": order["status"],
            "created_at": order["created_at"],
            "updated_at": order["updated_at"],
        }

    async def list_orders_by_buyer(self, buyer_id: str) -> list[dict]:
        """List all orders for a buyer."""
        orders = await self.order_repo.list_orders_by_buyer(buyer_id)
        return [
            {
                "order_id": order["id"],
                "negotiation_id": order["negotiation_id"],
                "buyer_id": order["buyer_id"],
                "seller_id": order["seller_id"],
                "product_id": order["product_id"],
                "final_price": order["final_price"],
                "status": order["status"],
                "created_at": order["created_at"],
                "updated_at": order["updated_at"],
            }
            for order in orders
        ]

    async def list_orders_by_seller(self, seller_id: str) -> list[dict]:
        """List all orders for a seller."""
        orders = await self.order_repo.list_orders_by_seller(seller_id)
        return [
            {
                "order_id": order["id"],
                "negotiation_id": order["negotiation_id"],
                "buyer_id": order["buyer_id"],
                "seller_id": order["seller_id"],
                "product_id": order["product_id"],
                "final_price": order["final_price"],
                "status": order["status"],
                "created_at": order["created_at"],
                "updated_at": order["updated_at"],
            }
            for order in orders
        ]
