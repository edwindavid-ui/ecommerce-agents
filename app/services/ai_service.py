from app.ai.orchestration import AIOrchestrator
from app.ai.prompts import PromptTemplates
from app.ai.providers import get_llm_provider


class AIService:
    def __init__(self, orchestrator: AIOrchestrator = None):
        if orchestrator is None:
            provider = get_llm_provider()
            orchestrator = AIOrchestrator(provider=provider)
        self.orchestrator = orchestrator
        self.prompts = PromptTemplates()

    async def analyze_products_for_buyer(self, requirement: str, candidates: list[dict]) -> dict:
        """
        Use AI to analyze products and recommend best choice.
        """
        prompt = self.prompts.buyer_analyze_products(requirement, candidates)
        response = self.orchestrator.call_with_tools(prompt)
        return response

    async def evaluate_offer_as_seller(self, offer_price: float, min_price: float, product_name: str) -> dict:
        """
        Use AI to evaluate if an offer is acceptable.
        Backend validates the decision against business rules.
        """
        prompt = self.prompts.seller_evaluate_offer(offer_price, min_price, product_name)
        response = self.orchestrator.call_with_tools(prompt)
        return response

    async def generate_counter_offer(self, buyer_offer: float, seller_min: float, seller_target: float) -> dict:
        """
        Use AI to suggest a counter-offer price.
        Backend validates the price is within acceptable range.
        """
        prompt = self.prompts.negotiation_counter_offer(buyer_offer, seller_min, seller_target)
        response = self.orchestrator.call_with_tools(prompt)
        
        # Validate that counter price is reasonable
        if "offer_price" in response:
            if response["offer_price"] < seller_min:
                raise ValueError("AI suggested price below seller minimum")
        
        return response
