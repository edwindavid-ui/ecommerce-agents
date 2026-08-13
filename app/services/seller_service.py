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
    def __init__(self, inventory_repository: InventoryRepository):
        self.repo = inventory_repository

    async def create_inventory(self, product_id: str, quantity: int) -> dict:
        existing = await self.repo.get_inventory_by_product_id(product_id)
        if existing:
            raise ValueError("Inventory already exists for this product")
        return await self.repo.create_inventory(product_id, quantity)

    async def get_inventory_by_product_id(self, product_id: str) -> dict:
        inv = await self.repo.get_inventory_by_product_id(product_id)
        if not inv:
            raise ValueError("Inventory not found for this product")
        return inv
