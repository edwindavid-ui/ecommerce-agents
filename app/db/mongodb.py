from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import get_settings

import os
from dotenv import load_dotenv

load_dotenv()

# Fetch MongoDB URI from your .env file
MONGO_DETAILS = os.environ.get("MONGODB_URI", "mongodb://localhost:27017")

client = AsyncIOMotorClient(MONGO_DETAILS)
database = client.my_fastapi_db
user_collection = database.get_collection("users_collection")


async def ping_db() -> bool:
    try:
        await client.admin.command("ping")
        return True
    except Exception as e:
        print(f"Database ping failed: {e}")
        return False
