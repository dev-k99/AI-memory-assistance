"""
DuckDuckGo web search tool — no API key required.
"""

from __future__ import annotations

from duckduckgo_search import DDGS
from langchain_core.tools import tool


@tool
def search_web(query: str) -> str:
    """Search the internet for current information, news, or facts not in training data."""
    try:
        results = list(DDGS().text(query, max_results=4))
        if not results:
            return "No results found."
        return "\n\n".join(
            f"{r['title']}\n{r['body']}\nSource: {r['href']}" for r in results
        )
    except Exception as exc:
        return f"Search failed: {exc}"
