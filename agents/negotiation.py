from agents.buyer import BuyerAgent
from agents.seller import SellerAgent

def run_negotiation(buyer: BuyerAgent, seller: SellerAgent, max_rounds: int = 5) -> dict:
    history = []

    for round_num in range(1, max_rounds + 1):
        offer = buyer.make_offer()
        response = seller.evaluate_offer(offer)

        history.append({
            "round": round_num,
            "buyer_offer": offer,
            "seller_decision": response["decision"],
            "seller_price": response["price"]
        })

        if response["decision"] == "accept":
            return {
                "status": "deal",
                "final_price": response["price"],
                "rounds": round_num,
                "history": history
            }

        buyer.revise_offer(response["price"])

    return {
        "status": "no_deal",
        "rounds": max_rounds,
        "history": history
    }