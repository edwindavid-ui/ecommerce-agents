from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import get_settings


settings = get_settings()

client = AsyncIOMotorClient(settings.mongo_url)
db = client[settings.mongo_db_name]


async def ping_db() -> bool:
    try:
        await client.admin.command("ping")
        return True
    except Exception:
        return False
