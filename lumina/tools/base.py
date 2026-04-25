from typing import Any, Callable, Dict, List, Optional, Type
from pydantic import BaseModel, Field

class Tool(BaseModel):
    name: str
    description: str
    parameters: Type[BaseModel]
    func: Callable

    def execute(self, **kwargs) -> Any:
        # Validate parameters
        params = self.parameters(**kwargs)
        return self.func(**params.dict())

class ToolRegistry:
    def __init__(self):
        self.tools: Dict[str, Tool] = {}

    def register(self, tool: Tool):
        self.tools[tool.name] = tool

    def get_tool(self, name: str) -> Optional[Tool]:
        return self.tools.get(name)

    def to_gemini_tools(self) -> List[Dict[str, Any]]:
        gemini_tools = []
        for name, tool in self.tools.items():
            schema = tool.parameters.schema()
            gemini_tools.append({
                "name": name,
                "description": tool.description,
                "parameters": {
                    "type": "object",
                    "properties": schema.get("properties", {}),
                    "required": schema.get("required", [])
                }
            })
        return gemini_tools
