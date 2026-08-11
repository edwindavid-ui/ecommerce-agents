from fastapi import FastAPI
from agents.buyer import BuyerAgent
from agents.seller import SellerAgent
from agents.negotiation import run_negotiation
from agents.recommender import RecommenderAgent

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "E-commerce agent system running"}

@app.post("/negotiate")
def negotiate(max_budget: float, list_price: float, min_price: float):
    buyer = BuyerAgent(max_budget=max_budget)
    seller = SellerAgent(product_name="demo product", list_price=list_price, min_price=min_price)
    result = run_negotiation(buyer, seller)
    return result

@app.get("/recommend")
async def recommend(category: str = None, max_price: float = None):
    recommender = RecommenderAgent()
    results = await recommender.recommend(category=category, max_price=max_price)
    return results