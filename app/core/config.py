import os
from functools import lru_cache

from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "ecommerce-agents"
    environment: str = os.getenv("APP_ENV", "development")
    mongo_url: str = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    mongo_db_name: str = os.getenv("MONGO_DB_NAME", "ecommerce_agents")
    api_version: str = "/api/v1"


@lru_cache
def get_settings() -> Settings:
    return Settings()
