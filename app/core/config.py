import os
from functools import lru_cache

from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "ecommerce-agents"
    environment: str = os.getenv("APP_ENV", "development")
    mongo_url: str = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    mongo_db_name: str = os.getenv("MONGO_DB_NAME", "ecommerce_agents")
    api_version: str = "/api/v1"
    # AI Provider Configuration
    ai_provider: str = os.getenv("AI_PROVIDER", "mock")  # Options: mock, gemini, openai
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4")


@lru_cache
def get_settings() -> Settings:
    return Settings()
