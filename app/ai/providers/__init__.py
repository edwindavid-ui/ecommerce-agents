from app.ai.providers.mock_provider import BaseLLMProvider, MockLLMProvider, GeminiProvider
from app.core.config import get_settings


def get_llm_provider() -> BaseLLMProvider:
    """
    Factory function to instantiate the correct LLM provider based on config.
    
    Configuration via environment variables:
    - AI_PROVIDER: "mock", "gemini", or "openai" (default: "mock")
    - GEMINI_API_KEY: Your Google Gemini API key
    - GEMINI_MODEL: Gemini model name (default: "gemini-2.0-flash")
    - OPENAI_API_KEY: Your OpenAI API key
    - OPENAI_MODEL: OpenAI model name (default: "gpt-4")
    """
    settings = get_settings()
    
    if settings.ai_provider == "gemini":
        if not settings.gemini_api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required when AI_PROVIDER=gemini")
        return GeminiProvider(api_key=settings.gemini_api_key, model=settings.gemini_model)
    
    else:  # default to mock
        return MockLLMProvider()
