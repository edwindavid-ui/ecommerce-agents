import os
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = os.environ.get("MONGO_URL")

client = AsyncIOMotorClient(MONGO_URL)
db = client["ecommerce_agents"]
products_collection = db["products"]