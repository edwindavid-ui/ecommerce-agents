from app.db.mongodb import database

from app.db.repositories.negotiations import NegotiationRepository
from app.db.repositories.orders import OrderRepository
from app.db.repositories.jobs import JobRepository
from app.db.repositories.buyer_agents import BuyerTaskRepository, BuyerAgentStateRepository
from app.db.repositories.seller_agents import SellerAgentRepository
from app.db.repositories.products import ProductRepository
from app.db.repositories.sellers import SellerRepository, InventoryRepository
from app.db.repositories.recommendations import RecommendationRepository

# Shared in-memory repository instances
negotiation_repo = NegotiationRepository(collection=database.get_collection("negotiations"))
order_repo = OrderRepository(collection=database.get_collection("orders"))
job_repo = JobRepository(collection=database.get_collection("jobs"))
buyer_task_repo = BuyerTaskRepository(collection=database.get_collection("buyer_tasks"))
buyer_agent_state_repo = BuyerAgentStateRepository(collection=database.get_collection("buyer_agents"))
seller_agent_repo = SellerAgentRepository(collection=database.get_collection("seller_agents"))
product_repo = ProductRepository(collection=database.get_collection("products"))
seller_repo = SellerRepository(collection=database.get_collection("sellers"))
inventory_repo = InventoryRepository(collection=database.get_collection("inventory"))
recommendation_repo = RecommendationRepository(collection=database.get_collection("recommendations"))
