from agents.database import products_collection

class RecommenderAgent:
    async def recommend(self, category: str = None, max_price: float = None) -> list:
        query = {}

        if category:
            query["category"] = category

        if max_price is not None:
            query["price"] = {"$lte": max_price}

        cursor = products_collection.find(query)
        results = []
        async for product in cursor:
            product["_id"] = str(product["_id"])
            results.append(product)

        return results