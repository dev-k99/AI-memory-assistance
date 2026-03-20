"""
RAG retrieval tool — queries the ChromaDB knowledge base.
"""

from langchain_core.tools import tool


@tool
def retrieve_from_documents(query: str) -> str:
    """Retrieve relevant information from the uploaded knowledge base documents. Use this when the user asks about documents they have uploaded or asks about topics that may be in the knowledge base."""
    from rag.pipeline import retrieve_context
    return retrieve_context(query)
