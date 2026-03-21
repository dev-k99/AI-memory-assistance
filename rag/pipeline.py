"""
RAG Pipeline — ChromaDB + HuggingFace sentence-transformers
Fully local, no API key required for embeddings.
"""

import os
import streamlit as st
from pathlib import Path
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

CHROMA_DIR = Path(__file__).parent.parent / "chroma_db"
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
SAMPLE_DOCS_DIR = Path(__file__).parent.parent / "sample_docs"


@st.cache_resource(show_spinner="Loading embedding model...")
def _get_embeddings():
    return HuggingFaceEmbeddings(
        model_name=EMBED_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )


@st.cache_resource(show_spinner=False)
def get_vectorstore() -> Chroma:
    embeddings = _get_embeddings()
    vs = Chroma(
        collection_name="memos_knowledge",
        embedding_function=embeddings,
        persist_directory=str(CHROMA_DIR),
    )
    # Auto-ingest sample docs on first load
    _auto_ingest_samples(vs)
    return vs


def _auto_ingest_samples(vs: Chroma):
    """Ingest bundled sample docs if the vectorstore is empty."""
    if vs._collection.count() > 0:
        return
    docs = []
    for f in SAMPLE_DOCS_DIR.glob("*.md"):
        text = f.read_text(encoding="utf-8")
        docs.append(Document(page_content=text, metadata={"source": f.name}))
    if docs:
        _add_documents(vs, docs)


def ingest_uploaded_files(uploaded_files) -> int:
    """
    Accept Streamlit UploadedFile objects (PDF, TXT, MD).
    Returns the number of chunks added.
    """
    from rag.ingest import load_uploaded_file

    vs = get_vectorstore()
    all_docs: list[Document] = []
    for uf in uploaded_files:
        all_docs.extend(load_uploaded_file(uf))
    if not all_docs:
        return 0
    return _add_documents(vs, all_docs)


def _add_documents(vs: Chroma, docs: list[Document]) -> int:
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(docs)
    vs.add_documents(chunks)
    return len(chunks)


def retrieve_context(query: str, k: int = 4) -> str:
    """Return top-k relevant chunks as a formatted string."""
    vs = get_vectorstore()
    results = vs.similarity_search(query, k=k)
    if not results:
        return "No relevant documents found in the knowledge base."
    parts = []
    for i, doc in enumerate(results, 1):
        src = doc.metadata.get("source", "unknown")
        parts.append(f"[{i}] (source: {src})\n{doc.page_content}")
    return "\n\n".join(parts)


def get_chunk_count() -> int:
    vs = get_vectorstore()
    return vs._collection.count()
