from typing import Any, Callable, Optional


class ToolRegistry:
    def __init__(self):
        self.tools: dict[str, Callable] = {}
        self.tool_descriptions: dict[str, str] = {}

    def register_tool(self, name: str, func: Callable, description: str = "") -> None:
        if name in self.tools:
            raise ValueError(f"Tool '{name}' is already registered")
        self.tools[name] = func
        self.tool_descriptions[name] = description

    def call_tool(self, tool_name: str, parameters: dict) -> Any:
        if tool_name not in self.tools:
            raise ValueError(f"Tool '{tool_name}' not found")
        func = self.tools[tool_name]
        return func(**parameters)

    def get_tool_list(self) -> list[dict]:
        return [
            {"name": name, "description": self.tool_descriptions.get(name, "")}
            for name in self.tools.keys()
        ]

    def is_tool_allowed(self, tool_name: str) -> bool:
        return tool_name in self.tools
