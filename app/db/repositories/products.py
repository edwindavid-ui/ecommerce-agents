class ProductRepository:

    def __init__(self, collection):
        self.collection = collection

    def build_filters(self, category: str | None = None, max_price: float | None = None):
            filters: dict[str, Any] = {}
            if category:
                filters["category"] = category
            if max_price is not None:
                filters["price"] = {"$lte": max_price}
            return filters

    async def list_products(self, category: str | None = None, max_price: float | None = None):
        query = self.build_filters(category=category, max_price=max_price)
        cursor = self.collection.find(query)
        raw_products = await cursor.to_list(length=100)
        
        products = []
        for doc in raw_products:
            if "_id" in doc:
                doc["id"] = str(doc["_id"])
                del doc["_id"]
            products.append(doc)
        return products

    async def create_product(self, product_dict: dict) -> dict:

        data_to_insert = product_dict.copy()

        data_to_insert.pop("_id", None)
        data_to_insert.pop("id", None)

        result = await self.collection.insert_one(data_to_insert)

        created_product = data_to_insert.copy()
        created_product["id"] = str(result.inserted_id)
        created_product.pop("_id", None)

        return created_product