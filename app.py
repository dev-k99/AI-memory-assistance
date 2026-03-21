"""
MemOS — The Memory Operating System for AI.
Agentic chatbot with persistent memory, RAG, and real-time web search.
Stack: LangGraph · Groq · ChromaDB · PostgreSQL · LangSmith
"""

from __future__ import annotations

import os
import uuid

import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

load_dotenv()

_TOOL_LABELS: dict[str, str] = {
    "search_web": "Web Search",
    "retrieve_from_documents": "Knowledge Base",
}

st.set_page_config(
    page_title="MemOS",
    page_icon="M",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inject global CSS once
st.markdown(
    """
    <style>
    /* Tighten default Streamlit padding */
    .block-container { padding-top: 0.75rem; padding-bottom: 1rem; }

    /* Version badge */
    .memos-badge {
        display: inline-block;
        background: #6C63FF;
        color: #fff;
        padding: 3px 12px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 0.04em;
    }

    /* Sidebar section headers */
    .sidebar-label {
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #A0AEC0;
        margin-bottom: 4px;
    }

    /* Tool-use indicator chips rendered above assistant responses */
    .tool-chip {
        display: inline-flex;
        align-items: center;
        background: rgba(108,99,255,0.10);
        border: 1px solid rgba(108,99,255,0.25);
        color: #9B94FF;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 500;
        margin: 0 6px 8px 0;
        letter-spacing: 0.02em;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def get_config() -> dict[str, str]:
    """
    Resolve runtime configuration.
    Priority: Streamlit secrets (production) > environment variables (local).
    Also propagates LangSmith env vars before agent.py is imported.
    """
    def _get(key: str, default: str = "") -> str:
        try:
            return st.secrets.get(key, os.getenv(key, default)) or default
        except Exception:
            return os.getenv(key, default) or default

    config = {
        "groq_api_key": _get("GROQ_API_KEY"),
        "database_url": _get("DATABASE_URL"),
        "langchain_api_key": _get("LANGCHAIN_API_KEY"),
        "tavily_api_key": _get("TAVILY_API_KEY"),
    }

    if config["tavily_api_key"]:
        os.environ["TAVILY_API_KEY"] = config["tavily_api_key"]

    if config["langchain_api_key"]:
        os.environ["LANGCHAIN_API_KEY"] = config["langchain_api_key"]
        os.environ["LANGCHAIN_TRACING_V2"] = _get("LANGCHAIN_TRACING_V2", "true")
        os.environ["LANGCHAIN_PROJECT"] = _get("LANGCHAIN_PROJECT", "memos")

    return config


def _render_welcome() -> str | None:
    """
    Render the welcome card with clickable suggestion chips.
    Returns the suggestion text if a chip was clicked, else None.
    """
    st.markdown(
        """
        <div style="
            margin: 1.5rem auto 1rem;
            max-width: 520px;
            background: #1E2130;
            border: 1px solid rgba(108,99,255,0.25);
            border-radius: 14px;
            padding: 1.25rem 1.5rem 1rem;
            text-align: center;
        ">
            <h3 style="margin: 0 0 0.3rem; font-size: 1.1rem;">Welcome to MemOS</h3>
            <p style="color: #A0AEC0; font-size: 0.82rem; line-height: 1.4; margin: 0;">
                Persistent memory &nbsp;·&nbsp; Web search &nbsp;·&nbsp; Document Q&amp;A
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    col1, col2, col3 = st.columns(3)
    if col1.button("What is RAG?", use_container_width=True):
        return "What is RAG?"
    if col2.button("Latest AI news", use_container_width=True):
        return "Search for the latest AI news"
    if col3.button("What do you remember?", use_container_width=True):
        return "What do you remember about me from past sessions?"
    return None


def main() -> None:
    config = get_config()

    if not config["groq_api_key"] or not config["database_url"]:
        st.error("Missing required configuration.")
        st.info(
            "**Local development:** copy `env.example` to `.env` and fill in values.\n\n"
            "**Streamlit Cloud:** add secrets under App Settings > Secrets."
        )
        st.stop()

    # Lazy imports — deferred so a config error surfaces before heavy model loading.
    from agent import build_agent, clear_session, get_pg_history, run_response
    from rag.pipeline import ingest_uploaded_files

    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    if "messages" not in st.session_state:
        st.session_state.messages = []

    agent = build_agent(config["groq_api_key"])

    # ── Header ────────────────────────────────────────────────────────────────
    st.markdown(
        "<div style='display:flex;align-items:center;gap:10px;padding-bottom:2px'>"
        "<span style='font-size:1.6rem;font-weight:700;line-height:1'>MemOS</span>"
        "<span class='memos-badge'>v2.0</span>"
        "</div>",
        unsafe_allow_html=True,
    )
    st.caption(
        "Memory Operating System &nbsp;·&nbsp; llama-3.1-8b-instant &nbsp;·&nbsp; "
        "LangGraph &nbsp;·&nbsp; ChromaDB &nbsp;·&nbsp; PostgreSQL",
        unsafe_allow_html=True,
    )

    # ── Sidebar ───────────────────────────────────────────────────────────────
    with st.sidebar:
        # Load session history — only surface errors, not counts
        msgs: list = []
        try:
            history = get_pg_history(st.session_state.session_id, config["database_url"])
            msgs = history.messages
        except Exception as exc:
            st.error(f"Database: {exc}")

        st.divider()

        # Knowledge Base
        st.markdown("<p class='sidebar-label'>Knowledge Base</p>", unsafe_allow_html=True)
        uploaded = st.file_uploader(
            "Upload documents",
            type=["pdf", "txt", "md"],
            accept_multiple_files=True,
            label_visibility="collapsed",
            help="Upload PDF, TXT, or Markdown files to add them to the knowledge base.",
        )
        if uploaded and st.button("Ingest Documents", use_container_width=True, type="primary"):
            with st.spinner("Chunking and embedding..."):
                n = ingest_uploaded_files(uploaded)
            st.success(f"Added {n} chunks.")
            st.rerun()

        st.divider()

        # Session controls
        col_clear, col_new = st.columns(2)
        with col_clear:
            if st.button("Clear Memory", use_container_width=True):
                try:
                    clear_session(st.session_state.session_id, config["database_url"])
                    st.session_state.messages = []
                    st.rerun()
                except Exception as exc:
                    st.error(str(exc))
        with col_new:
            if st.button("New Chat", use_container_width=True, type="primary"):
                st.session_state.session_id = str(uuid.uuid4())
                st.session_state.messages = []
                st.rerun()

        # Conversation history — collapsed, for power users
        if msgs:
            st.divider()
            with st.expander(f"History ({len(msgs)} messages)"):
                for i, msg in enumerate(msgs):
                    role = "You" if isinstance(msg, HumanMessage) else "MemOS"
                    preview = msg.content[:120] + ("..." if len(msg.content) > 120 else "")
                    st.caption(f"**{role}:** {preview}")
                    if i < len(msgs) - 1:
                        st.divider()

    # ── Chat area ─────────────────────────────────────────────────────────────

    # Welcome screen with clickable suggestion chips (shown only when no messages)
    prompt_from_chip: str | None = None
    if not st.session_state.messages:
        prompt_from_chip = _render_welcome()

    # Render existing conversation history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # ── Input ─────────────────────────────────────────────────────────────────
    if prompt := (prompt_from_chip or st.chat_input("Ask anything — I remember everything...")):
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            try:
                with st.spinner(""):
                    response_text, tools_used = run_response(
                        agent,
                        prompt,
                        st.session_state.session_id,
                        config["database_url"],
                    )
            except Exception as exc:
                st.error(f"Error generating response: {exc}")
                st.session_state.messages.append(
                    {"role": "assistant", "content": f"Error: {exc}"}
                )
            else:
                # Show which tools were used (deduplicated, known tools only)
                chips = "".join(
                    f"<span class='tool-chip'>{_TOOL_LABELS[t]}</span>"
                    for t in dict.fromkeys(tools_used)
                    if t in _TOOL_LABELS
                )
                if chips:
                    st.markdown(chips, unsafe_allow_html=True)
                st.markdown(response_text or "_No response generated._")
                st.session_state.messages.append(
                    {"role": "assistant", "content": response_text}
                )


if __name__ == "__main__":
    main()
