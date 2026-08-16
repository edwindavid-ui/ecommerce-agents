from app.ai.prompts import PromptTemplates
from app.ai.providers import get_llm_provider

class AIService:
    def __init__(self, provider = None):
        self.provider = provider or get_llm_provider()
        self.prompts = PromptTemplates()

    async def analyze_products_for_buyer(self, requirement: str, candidates: list[dict]) -> dict:
        prompt = self.prompts.buyer_analyze_products(requirement, candidates)
        return self.provider.call_model(prompt)

    async def evaluate_offer_as_seller(self, offer_price: float, min_price: float, product_name: str) -> dict:
        prompt = self.prompts.seller_evaluate_offer(offer_price, min_price, product_name)
        return self.provider.call_model(prompt)

    async def generate_counter_offer(self, buyer_offer: float, seller_min: float, seller_target: float) -> dict:
        prompt = self.prompts.negotiation_counter_offer(buyer_offer, seller_min, seller_target)
        return self.provider.call_model(prompt)