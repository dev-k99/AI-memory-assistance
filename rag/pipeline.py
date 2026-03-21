"""
RAG pipeline — ChromaDB vector store with HuggingFace sentence-transformers embeddings.
Embeddings run fully locally; no API key required.
"""

from __future__ import annotations

from pathlib import Path

import streamlit as st
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

CHROMA_DIR = Path(__file__).parent.parent / "chroma_db"
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
SAMPLE_DOCS_DIR = Path(__file__).parent.parent / "sample_docs"

_SPLITTER = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)


@st.cache_resource(show_spinner="Loading embedding model...")
def _get_embeddings() -> HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings(
        model_name=EMBED_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )


@st.cache_resource(show_spinner=False)
def get_vectorstore() -> Chroma:
    vs = Chroma(
        collection_name="memos_knowledge",
        embedding_function=_get_embeddings(),
        persist_directory=str(CHROMA_DIR),
    )
    _auto_ingest_samples(vs)
    return vs


def _auto_ingest_samples(vs: Chroma) -> None:
    """Seed the vectorstore with bundled sample docs on first boot."""
    if vs._collection.count() > 0:
        return
    docs = [
        Document(page_content=f.read_text(encoding="utf-8"), metadata={"source": f.name})
        for f in SAMPLE_DOCS_DIR.glob("*.md")
    ]
    if docs:
        _add_documents(vs, docs)


def ingest_uploaded_files(uploaded_files) -> int:
    """
    Chunk and embed Streamlit UploadedFile objects (PDF, TXT, MD).
    Returns the number of chunks added to the vectorstore.
    """
    from rag.ingest import load_uploaded_file  # deferred to avoid circular import

    vs = get_vectorstore()
    docs: list[Document] = []
    for uf in uploaded_files:
        docs.extend(load_uploaded_file(uf))
    return _add_documents(vs, docs) if docs else 0


def _add_documents(vs: Chroma, docs: list[Document]) -> int:
    chunks = _SPLITTER.split_documents(docs)
    vs.add_documents(chunks)
    return len(chunks)


def retrieve_context(query: str, k: int = 4) -> str:
    """Return the top-k most relevant chunks as a formatted string."""
    results = get_vectorstore().similarity_search(query, k=k)
    if not results:
        return "No relevant documents found in the knowledge base."
    return "\n\n".join(
        f"[{i}] (source: {doc.metadata.get('source', 'unknown')})\n{doc.page_content}"
        for i, doc in enumerate(results, 1)
    )


def get_chunk_count() -> int:
    return get_vectorstore()._collection.count()
