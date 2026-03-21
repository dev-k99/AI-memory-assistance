"""
Document loaders for RAG ingestion.
Supports PDF, TXT, and Markdown files.
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_core.documents import Document


def load_uploaded_file(uploaded_file) -> list[Document]:
    """
    Load a Streamlit UploadedFile into LangChain Documents.
    Supports .pdf, .txt, and .md extensions.
    """
    suffix = Path(uploaded_file.name).suffix.lower()
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.getvalue())
        tmp_path = tmp.name

    try:
        loader = PyPDFLoader(tmp_path) if suffix == ".pdf" else TextLoader(tmp_path, encoding="utf-8")
        docs = loader.load()
        for doc in docs:
            doc.metadata["source"] = uploaded_file.name
        return docs
    finally:
        Path(tmp_path).unlink(missing_ok=True)
