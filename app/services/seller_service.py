from app.db.repositories.sellers import SellerRepository, InventoryRepository
from app.schemas.seller import SellerCreate


class SellerService:
    def __init__(self, seller_repository: SellerRepository):
        self.repo = seller_repository

    async def create_seller(self, user_id: str, seller_data: SellerCreate) -> dict:
        existing = await self.repo.get_seller_by_user_id(user_id)
        if existing:
            raise ValueError("Seller profile already exists for this user")
        return await self.repo.create_seller(user_id, seller_data)

    async def get_seller_by_user_id(self, user_id: str) -> dict:
        seller = await self.repo.get_seller_by_user_id(user_id)
        if not seller:
            raise ValueError("Seller profile not found")
        return seller


class InventoryService:
    def __init__(self, inventory_repository):
        self.inventory_repo = inventory_repository

    async def create_inventory(self, product_id: str, seller_id: str, quantity: int) -> dict:
        existing = await self.inventory_repo.get_inventory_by_seller_and_product(seller_id, product_id)
        if existing:
            raise ValueError("Inventory already exists for this product and seller")
        return await self.inventory_repo.create_inventory(product_id, seller_id, quantity)

    async def get_inventory(self, inventory_id: str) -> dict:
        inv = await self.inventory_repo.get_inventory_by_id(inventory_id)
        if not inv:
            raise ValueError("Inventory not found")
        return inv

    async def update_inventory(self, inventory_id: str, quantity: int) -> dict:
        updated = await self.inventory_repo.update_quantity(inventory_id, quantity)
        if not updated:
            raise ValueError("Inventory not found or update failed")
        return updated

    async def reserve_stock(self, inventory_id: str, quantity: int) -> dict:
        updated = await self.inventory_repo.reserve_inventory(inventory_id, quantity)
        if not updated:
            raise ValueError("Failed to reserve stock. Insufficient available quantity or inventory not found.")
        return updated

    async def release_stock(self, inventory_id: str, quantity: int) -> dict:
        updated = await self.inventory_repo.release_inventory(inventory_id, quantity)
        if not updated:
            raise ValueError("Failed to release stock. Invalid reservation amount or inventory not found.")
        return updated
