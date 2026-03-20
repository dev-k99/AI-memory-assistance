"""
DuckDuckGo web search tool — no API key required.
"""

from langchain_core.tools import tool


@tool
def search_web(query: str) -> str:
    """Search the internet for current information, news, or facts you don't know."""
    try:
        from duckduckgo_search import DDGS
        results = DDGS().text(query, max_results=4)
        if not results:
            return "No results found."
        parts = []
        for r in results:
            parts.append(f"**{r['title']}**\n{r['body']}\nSource: {r['href']}")
        return "\n\n".join(parts)
    except Exception as e:
        return f"Search failed: {e}"
