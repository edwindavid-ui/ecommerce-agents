class ProductRepository:

    def __init__(self, collection):
        self.collection = collection

    async def list_products(
        self,
        category: str | None = None,
        max_price: float | None = None
    ) -> list[dict]:

        query = {}

        if category is not None:
            query["category"] = category

        if max_price is not None:
            query["price"] = {"$lte": max_price}

        raw_products = await self.collection.find(query).to_list(length=None)

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

        return created_product