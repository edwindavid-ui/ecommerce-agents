"""Shared repository instances for dependency injection across routers."""

from app.db.repositories.negotiations import NegotiationRepository
from app.db.repositories.orders import OrderRepository
from app.db.repositories.jobs import JobRepository
from app.db.repositories.buyer_agents import BuyerTaskRepository, BuyerAgentStateRepository
from app.db.repositories.seller_agents import SellerAgentRepository
from app.db.repositories.products import ProductRepository
from app.db.repositories.sellers import SellerRepository, InventoryRepository
from app.db.repositories.recommendations import RecommendationRepository

# Shared in-memory repository instances
negotiation_repo = NegotiationRepository(collection=None)
order_repo = OrderRepository(collection=None)
job_repo = JobRepository(collection=None)
buyer_task_repo = BuyerTaskRepository(collection=None)
buyer_agent_state_repo = BuyerAgentStateRepository(collection=None)
seller_agent_repo = SellerAgentRepository(collection=None)
product_repo = ProductRepository(collection=None)
seller_repo = SellerRepository(collection=None)
inventory_repo = InventoryRepository(collection=None)
recommendation_repo = RecommendationRepository(collection=None)
