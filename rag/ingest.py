"""
Document loaders for RAG ingestion.
Supports PDF, TXT, and Markdown files.
"""

import tempfile
import os
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader, TextLoader


def load_uploaded_file(uploaded_file) -> list[Document]:
    """
    Load a Streamlit UploadedFile into a list of LangChain Documents.
    Supports: .pdf, .txt, .md
    """
    suffix = "." + uploaded_file.name.split(".")[-1].lower()
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.getvalue())
        tmp_path = tmp.name

    try:
        if suffix == ".pdf":
            loader = PyPDFLoader(tmp_path)
        else:
            loader = TextLoader(tmp_path, encoding="utf-8")
        docs = loader.load()
        for doc in docs:
            doc.metadata["source"] = uploaded_file.name
        return docs
    finally:
        os.unlink(tmp_path)
