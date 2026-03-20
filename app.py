"""
MemOS — The Memory Operating System for AI
An agentic chatbot with persistent memory, RAG, and web search.
Built with LangGraph · Groq · ChromaDB · PostgreSQL · LangSmith
"""

import streamlit as st
import os
import uuid
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage

load_dotenv()


# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MemOS",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ── Configuration ─────────────────────────────────────────────────────────────
def get_config() -> dict:
    config = {}
    try:
        config["groq_api_key"] = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY"))
        config["database_url"] = st.secrets.get("DATABASE_URL", os.getenv("DATABASE_URL"))
        config["langchain_api_key"] = st.secrets.get(
            "LANGCHAIN_API_KEY", os.getenv("LANGCHAIN_API_KEY", "")
        )
    except Exception:
        config["groq_api_key"] = os.getenv("GROQ_API_KEY")
        config["database_url"] = os.getenv("DATABASE_URL")
        config["langchain_api_key"] = os.getenv("LANGCHAIN_API_KEY", "")

    # Push LangSmith vars into environment so agent.py picks them up
    if config["langchain_api_key"]:
        os.environ["LANGCHAIN_API_KEY"] = config["langchain_api_key"]
        os.environ["LANGCHAIN_TRACING_V2"] = st.secrets.get(
            "LANGCHAIN_TRACING_V2", os.getenv("LANGCHAIN_TRACING_V2", "true")
        )
    return config


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    config = get_config()

    if not config.get("groq_api_key") or not config.get("database_url"):
        st.error("Missing configuration")
        st.info(
            "**Local:** Copy `env.example` → `.env` and fill in values.\n\n"
            "**Streamlit Cloud:** Add secrets in App Settings → Secrets."
        )
        st.stop()

    # Lazy imports after config check (avoids slow model load on config error)
    from agent import build_agent, stream_response, clear_session, get_pg_history
    from rag.pipeline import ingest_uploaded_files, get_chunk_count

    # ── Session state ──────────────────────────────────────────────────────────
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    if "messages" not in st.session_state:
        st.session_state.messages = []

    agent = build_agent(config["groq_api_key"])

    # ── Header ─────────────────────────────────────────────────────────────────
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("# 🧠 MemOS")
        st.caption(
            "Memory Operating System · Groq llama-3.3-70b · LangGraph · ChromaDB · PostgreSQL"
        )
    with col2:
        st.markdown(
            "<div style='text-align:right; padding-top:10px'>"
            "<span style='background:#6C63FF;color:white;padding:4px 10px;"
            "border-radius:12px;font-size:13px'>v2.0</span></div>",
            unsafe_allow_html=True,
        )

    # ── Sidebar ────────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("## Session")
        st.info(f"**ID:** `{st.session_state.session_id[:8]}...`")

        # DB metrics
        try:
            history = get_pg_history(st.session_state.session_id, config["database_url"])
            msgs = history.messages
            st.success("Database connected")
            c1, c2 = st.columns(2)
            c1.metric("Messages", len(msgs))
            c2.metric("KB Chunks", get_chunk_count())
        except Exception as e:
            st.error(f"DB error: {e}")
            msgs = []

        st.divider()

        # ── Knowledge Base upload ──────────────────────────────────────────────
        st.markdown("### Knowledge Base")
        uploaded = st.file_uploader(
            "Upload documents (PDF, TXT, MD)",
            type=["pdf", "txt", "md"],
            accept_multiple_files=True,
            label_visibility="collapsed",
        )
        if uploaded and st.button("Ingest Documents", use_container_width=True):
            with st.spinner("Processing documents..."):
                n = ingest_uploaded_files(uploaded)
            st.success(f"Added {n} chunks to knowledge base")
            st.rerun()

        st.divider()

        # ── Memory viewer ──────────────────────────────────────────────────────
        st.markdown("### Session Memory")
        if msgs:
            with st.expander("View history", expanded=False):
                for i, msg in enumerate(msgs):
                    role = "You" if isinstance(msg, HumanMessage) else "MemOS"
                    st.caption(f"**{role}:** {msg.content[:120]}{'...' if len(msg.content) > 120 else ''}")
                    if i < len(msgs) - 1:
                        st.divider()
        else:
            st.caption("No messages yet.")

        st.divider()

        # ── Controls ───────────────────────────────────────────────────────────
        if st.button("Clear Memory", use_container_width=True):
            try:
                clear_session(st.session_state.session_id, config["database_url"])
                st.session_state.messages = []
                st.rerun()
            except Exception as e:
                st.error(str(e))

        if st.button("New Session", type="primary", use_container_width=True):
            st.session_state.session_id = str(uuid.uuid4())
            st.session_state.messages = []
            st.rerun()

        st.divider()

        # ── Settings / Observability ───────────────────────────────────────────
        with st.expander("Settings"):
            st.caption("**Model:** llama-3.3-70b-versatile")
            st.caption("**Embeddings:** all-MiniLM-L6-v2 (local)")
            st.caption("**Vector DB:** ChromaDB (local)")
            st.caption("**Memory DB:** PostgreSQL")
            env = "Production" if os.getenv("STREAMLIT_SHARING_MODE") else "Local"
            st.caption(f"**Environment:** {env}")

        with st.expander("Observability"):
            if config.get("langchain_api_key"):
                st.success("LangSmith tracing active")
                st.markdown("[View Traces ↗](https://smith.langchain.com)")
            else:
                st.info("Add `LANGCHAIN_API_KEY` to enable LangSmith tracing.")

    # ── Chat messages ──────────────────────────────────────────────────────────
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar="🧠" if message["role"] == "assistant" else None):
            st.markdown(message["content"])

    # ── Chat input ─────────────────────────────────────────────────────────────
    if prompt := st.chat_input("Ask anything — I remember everything..."):
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant", avatar="🧠"):
            try:
                response_text = st.write_stream(
                    stream_response(
                        agent,
                        prompt,
                        st.session_state.session_id,
                        config["database_url"],
                    )
                )
                st.session_state.messages.append(
                    {"role": "assistant", "content": response_text}
                )
            except Exception as e:
                err = f"Error: {e}"
                st.error(err)
                st.session_state.messages.append({"role": "assistant", "content": err})

    # ── Footer ─────────────────────────────────────────────────────────────────
    st.divider()
    st.caption(
        "MemOS remembers every conversation across sessions. "
        "Ask it to search the web or query your uploaded documents. "
        "Powered by [Groq](https://groq.com) · [LangGraph](https://langchain-ai.github.io/langgraph/) · "
        "[ChromaDB](https://www.trychroma.com) · [LangSmith](https://smith.langchain.com)"
    )


if __name__ == "__main__":
    main()
