class SellerAgent:
    def __init__(self, product_name: str, list_price: float, min_price: float):
        self.product_name = product_name
        self.list_price = list_price
        self.min_price = min_price

    def evaluate_offer(self, offer: float) -> dict:
        if offer >= self.min_price:
            return {"decision": "accept", "price": offer}
        else:
            counter = (offer + self.min_price) / 2
            return {"decision": "counter", "price": round(counter, 2)}
