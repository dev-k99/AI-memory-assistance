"""
Tavily web search tool — reliable cloud search designed for LLM integrations.
"""

from __future__ import annotations

import os

from langchain_core.tools import tool
from tavily import TavilyClient


@tool
def search_web(query: str) -> str:
    """Search the internet for current information, news, or facts not in training data."""
    api_key = os.getenv("TAVILY_API_KEY", "")
    if not api_key:
        return "Search unavailable: TAVILY_API_KEY not set."
    try:
        client = TavilyClient(api_key=api_key)
        response = client.search(query, max_results=4)
        results = response.get("results", [])
        if not results:
            return "No results found."
        return "\n\n".join(
            f"{r['title']}\n{r['content']}\nSource: {r['url']}" for r in results
        )
    except Exception as exc:
        return f"Search failed: {exc}"
