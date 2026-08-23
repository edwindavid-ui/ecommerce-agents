class PromptTemplates:
    @staticmethod
    def buyer_analyze_products(requirement: str, candidates: list[dict]) -> str:
        candidates_text = "\n".join([
            f"- {c.get('name')} (${c.get('price')}): {c.get('description', 'N/A')}"
            for c in candidates
        ])
        return f"""
Analyze the following product candidates against the buyer's requirement.

Buyer Requirement: {requirement}

Product Candidates:
{candidates_text}

Provide reasoning for the best choice and your confidence level.
Return a structured response with reasoning, decision (product name), and confidence (0-1).
"""

    @staticmethod
    def seller_evaluate_offer(offer_price: float, min_price: float, product_name: str) -> str:
        return f"""
Evaluate the following offer from a buyer for {product_name}.

Offer Price: ${offer_price}
Seller Minimum Price: ${min_price}

Decide whether to accept, counter, or reject the offer.
Consider the negotiation strategy and market conditions.
Return your reasoning, decision, and confidence level.
"""

    @staticmethod
    def negotiation_counter_offer(buyer_offer: float, seller_min: float, seller_target: float) -> str:
        return f"""
Generate a counter-offer strategy for negotiation.

Buyer's Current Offer: ${buyer_offer}
Seller Minimum Price: ${seller_min}
Seller Target Price: ${seller_target}

CRITICAL: You MUST respond ONLY with a valid JSON object. Do not include markdown formatting.
You must use exactly these keys:
- "counter_price": (a numeric float between the buyer offer and your target)
- "reasoning": (a short string message explaining the price to the buyer)
- "confidence": (a numeric float between 0 and 1)
- "decision": "counter"
"""
