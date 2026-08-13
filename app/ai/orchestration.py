from typing import Any

from app.ai.tools.registry import ToolRegistry
from app.ai.providers.mock_provider import BaseLLMProvider, MockLLMProvider
from app.ai.models.structured_output import StructuredResponse


class AIOrchestrator:
    def __init__(self, provider: BaseLLMProvider = None, tool_registry: ToolRegistry = None):
        self.provider = provider or MockLLMProvider()
        self.tool_registry = tool_registry or ToolRegistry()

    def call_with_tools(self, prompt: str, allowed_tools: list[str] = None) -> dict:
        """
        Call LLM with access to validated tools.
        Only tools in allowed_tools list can be invoked.
        """
        available_tools = self.tool_registry.get_tool_list()
        
        if allowed_tools:
            available_tools = [t for t in available_tools if t["name"] in allowed_tools]

        # Call LLM with tool list
        response = self.provider.call_model(prompt)

        # Validate response schema
        try:
            validated = StructuredResponse(**response)
        except Exception as exc:
            raise ValueError(f"LLM response did not match expected schema: {exc}")

        return validated.model_dump()

    def safe_tool_call(self, tool_name: str, parameters: dict) -> Any:
        """
        Safely execute a tool call with validation.
        """
        if not self.tool_registry.is_tool_allowed(tool_name):
            raise ValueError(f"Tool '{tool_name}' is not allowed")

        try:
            result = self.tool_registry.call_tool(tool_name, parameters)
        except Exception as exc:
            raise ValueError(f"Tool call failed: {exc}")

        return result
