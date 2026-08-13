from app.ai.tools.registry import ToolRegistry
from app.ai.models.structured_output import StructuredResponse
from app.ai.providers.mock_provider import MockLLMProvider


def test_tool_registry_can_register_and_call_tools():
    registry = ToolRegistry()
    
    def search_products(category: str, max_price: float) -> dict:
        return {"category": category, "max_price": max_price, "results": []}
    
    registry.register_tool("search_products", search_products)
    assert "search_products" in registry.tools
    
    result = registry.call_tool("search_products", {"category": "electronics", "max_price": 1000})
    assert result["category"] == "electronics"


def test_structured_response_validates_schema():
    response = StructuredResponse(
        reasoning="The best option is the laptop",
        decision="SELECT_LAPTOP",
        confidence=0.92,
    )
    
    assert response.reasoning == "The best option is the laptop"
    assert response.decision == "SELECT_LAPTOP"
    assert response.confidence == 0.92


def test_mock_llm_provider_returns_structured_output():
    provider = MockLLMProvider()
    
    prompt = "What product should the buyer choose?"
    response = provider.call_model(prompt)
    
    assert isinstance(response, dict)
    assert "reasoning" in response
    assert "decision" in response
    assert "confidence" in response
