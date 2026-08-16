from datetime import datetime, timezone
from bson import ObjectId

class OrderService:
    def __init__(
        self,
        order_repo,
        negotiation_repo,
        product_repo,
        inventory_repo
    ):
        self.order_repo = order_repo
        self.negotiation_repo = negotiation_repo
        self.product_repo = product_repo
        self.inventory_repo = inventory_repo

    async def create_from_negotiation(self, negotiation_id: str) -> dict:
        # 1. Fetch negotiation
        neg = await self.negotiation_repo.get_by_id(negotiation_id)
        if not neg:
            raise ValueError("Negotiation not found")
        
        if neg["status"] != "accepted":
            raise ValueError(f"Orders can only be created from accepted negotiations (Current status: {neg['status']})")

        # 2. Verify product exists
        product = await self.product_repo.get_product(neg["product_id"])
        if not product:
            raise ValueError("Product not found")

        quantity = neg.get("quantity", 1)
        unit_price = neg.get("current_offer") or neg.get("final_price")
        if not unit_price:
            raise ValueError("Invalid negotiated price found in negotiation record")

        total_price = unit_price * quantity

        # 3. Find associated inventory doc for this product and seller
        inventory_doc = await self.inventory_repo.collection.find_one({
            "product_id": neg["product_id"],
            "seller_id": neg["seller_id"]
        })

        if not inventory_doc:
            raise ValueError("Inventory record not found for this product and seller")

        inventory_id = inventory_doc["_id"]
        current_qty = inventory_doc.get("quantity", 0)

        # 4. Atomic stock deduction to prevent overselling
        # Ensures quantity is greater than or equal to what is being purchased
        updated_inventory = await self.inventory_repo.collection.find_one_and_update(
            {
                "_id": ObjectId(inventory_id),
                "quantity": {"$gte": quantity}
            },
            {
                "$inc": {"quantity": -quantity}
            },
            return_document=True
        )

        if not updated_inventory:
            raise ValueError("Insufficient stock available to fulfill this order.")

        # 5. Build and save the order
        order_data = {
            "buyer_id": neg["buyer_id"],
            "seller_id": neg["seller_id"],
            "product_id": neg["product_id"],
            "negotiation_id": negotiation_id,
            "quantity": quantity,
            "unit_price": unit_price,
            "total_price": total_price,
            "currency": neg.get("currency", "NGN"),
            "status": "confirmed"
        }

        created_order = await self.order_repo.create_order(order_data)

        # 6. Mark negotiation as completed
        await self.negotiation_repo.update_status(negotiation_id, "completed")

        return created_order