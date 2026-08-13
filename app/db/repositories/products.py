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
        return self.collection.find(query)
