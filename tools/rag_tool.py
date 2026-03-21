"""
RAG retrieval tool — queries the ChromaDB knowledge base.
"""

from __future__ import annotations

from langchain_core.tools import tool


@tool
def retrieve_from_documents(query: str) -> str:
    """
    Retrieve relevant information from the knowledge base.
    Use this when the user asks about uploaded documents or topics
    that may be covered in the knowledge base.
    """
    from rag.pipeline import retrieve_context  # deferred to avoid circular import
    return retrieve_context(query)
