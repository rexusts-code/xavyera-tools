from typing import List
from pydantic import BaseModel, Field
from .base import Tool
try:
    from duckduckgo_search import DDGS
except ImportError:
    DDGS = None

class SearchParams(BaseModel):
    query: str = Field(..., description="The search query.")

def web_search(query: str) -> str:
    if not DDGS:
        return "Error: duckduckgo-search package not installed."
    try:
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=5):
                results.append(f"Title: {r['title']}\nURL: {r['href']}\nSnippet: {r['body']}\n")
        return "\n".join(results) if results else "No results found."
    except Exception as e:
        return f"Error during search: {str(e)}"

def register_search_tools(registry):
    registry.register(Tool(
        name="web_search",
        description="Searches the web for information.",
        parameters=SearchParams,
        func=web_search
    ))
