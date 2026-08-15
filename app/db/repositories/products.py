from typing import Any


class ProductRepository:
    def __init__(self, collection: Any):
        self.collection = collection

    def build_filters(self, category: str | None = None, max_price: float | None = None) -> dict:
        filters: dict[str, Any] = {}

        if category:
            filters["category"] = category

        if max_price is not None:
            filters["price"] = {"$lte": max_price}

        return filters

    async def list_products(self, category: str | None = None, max_price: float | None = None):
        query = self.build_filters(category=category, max_price=max_price)
        cursor = self.collection.find(query)
        return await cursor.to_list(length=100)  # Limit to 100 results for simplicity

    async def create_product(self, product_dict: dict) -> dict:
        result = await self.collection.insert_one(product_dict)
        product_dict["id"] = str(result.inserted_id)
        return product_dict