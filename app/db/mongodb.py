from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import get_settings

from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

# Fetch MongoDB URI from your .env file
MONGO_DETAILS = os.environ.get("MONGODB_URI", "mongodb+srv://victorbankole11:unntouchable20.@cluster0.lhehf1s.mongodb.net/ecommerce-agent")

client = AsyncIOMotorClient(MONGO_DETAILS)
database = client.my_fastapi_db
user_collection = database.get_collection("users_collection")

settings = get_settings()

client = AsyncIOMotorClient(settings.mongo_url)
db = client[settings.mongo_db_name]


async def ping_db() -> bool:
    try:
        await client.admin.command("ping")
        return True
    except Exception:
        return False
