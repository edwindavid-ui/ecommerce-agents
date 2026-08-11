class BuyerAgent:
    def __init__(self, max_budget: float, starting_offer_ratio: float = 0.7):
        self.max_budget = max_budget
        self.current_offer = round(max_budget * starting_offer_ratio, 2)

    def make_offer(self) -> float:
        return self.current_offer

    def revise_offer(self, seller_counter: float):
        new_offer = min(self.max_budget, (self.current_offer + seller_counter) / 2)
        self.current_offer = round(new_offer, 2)
        return self.current_offer
