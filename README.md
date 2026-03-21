# MemOS — The Memory Operating System for AI

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.42+-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.3+-6C63FF)](https://langchain-ai.github.io/langgraph/)
[![Groq](https://img.shields.io/badge/Groq-llama--3.1--8b-F55036)](https://groq.com)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-RAG-00B4D8)](https://trychroma.com)
[![LangSmith](https://img.shields.io/badge/LangSmith-Traced-8B5CF6)](https://smith.langchain.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Neon-336791?logo=postgresql&logoColor=white)](https://neon.tech)
[![License](https://img.shields.io/badge/License-MIT-22C55E)](LICENSE)

**An agentic AI assistant that remembers everything, searches the web, and queries your documents — deployed at zero cost.**

[Landing Page](https://dev-k99.github.io/MemOS/) • [Live Demo](https://memos-v2-1.streamlit.app) • [Features](#features) • [Architecture](#architecture) • [Quickstart](#quickstart) • [Deploy](#deployment)

</div>

---

## What is MemOS?

MemOS is a full-stack AI engineering portfolio project demonstrating the core skills demanded in AI Engineer:

| Skill | Implementation |
|---|---|
| **RAG** | ChromaDB + HuggingFace `all-MiniLM-L6-v2` embeddings, PDF/TXT/MD upload |
| **Agentic AI** | Custom LangGraph `StateGraph` with `ToolNode` and conditional routing |
| **Tool Use** | Tavily web search, knowledge base retrieval injected as context |
| **Persistent Memory** | PostgreSQL via `SQLChatMessageHistory`, cross-session |
| **Observability** | LangSmith auto-tracing of every agent invocation |
| **Deployment** | Streamlit Cloud + Neon PostgreSQL — **$0/month** |

---

## Features

- **Persistent Long-Term Memory** — every conversation stored in PostgreSQL, survives app restarts and new sessions
- **RAG over your documents** — upload PDF/TXT/MD files; relevant chunks are retrieved and injected as context before every response
- **Live web search** — Tavily integration, reliable on cloud deployments
- **Custom LangGraph agent** — `StateGraph` built from scratch, not `create_react_agent`, giving full control over tool binding and message flow
- **LangSmith tracing** — full observability dashboard showing tool calls, latency, token usage
- **Auto-ingested demo docs** — pre-loaded AI knowledge base; works immediately without uploading anything
- **Tool-use indicators** — UI chips show when Web Search or Knowledge Base was used

---

## Architecture

```
User Input
    │
    ▼
Streamlit UI (app.py)
    │
    ├── RAG: retrieve_context(query) ──► ChromaDB ──► all-MiniLM-L6-v2
    │         (always runs, injected into system message)
    │
    ▼
LangGraph StateGraph (agent.py)
    │
    ├── agent_node ──► ChatGroq (llama-3.1-8b-instant)
    │                       │
    │              tool_calls? ──► ToolNode ──► search_web (Tavily)
    │                       │
    │              final response
    │
    ▼
PostgreSQL (Neon) ──► persist human + assistant messages
    │
    ▼
LangSmith ──► trace every invocation
```

### Key Design Decisions

- **Custom `StateGraph` instead of `create_react_agent`**: gives direct access to `bind_tools(parallel_tool_calls=False)`, which is required to prevent Groq's `failed_generation` errors on Llama models.
- **RAG as context injection, not a tool**: Llama models on Groq generate malformed XML-style tool calls intermittently. Injecting RAG context unconditionally into the system message is simpler and fully reliable.
- **No `MemorySaver` checkpointer**: using it alongside PostgreSQL history caused duplicate messages in the graph state, which corrupted tool call formatting. PostgreSQL is the sole source of truth.

---

## Project Structure

```
MemOS/
├── app.py                     # Streamlit UI — config, sidebar, chat handling
├── agent.py                   # LangGraph agent, PostgreSQL helpers, run_response
├── rag/
│   ├── pipeline.py            # ChromaDB vectorstore + HuggingFace embeddings
│   └── ingest.py              # Document loaders (PDF, TXT, MD)
├── tools/
│   └── search.py              # Tavily web search tool
├── sample_docs/               # Pre-ingested demo knowledge base
│   ├── ai_overview.md
│   └── about_memos.md
├── setup_database.py          # PostgreSQL schema initialisation
├── schema.sql                 # DB schema (message_store, sessions, triggers)
├── requirements.txt
├── env.example
├── .streamlit/config.toml     # Dark theme
└── docs/index.html            # GitHub Pages landing page
```

---

## Quickstart

### Prerequisites
- Python 3.11+
- Free [Groq API key](https://console.groq.com)
- Free [Neon](https://neon.tech) or any PostgreSQL database
- Free [Tavily API key](https://tavily.com) (1,000 searches/month)

### 1. Clone & Install
```bash
git clone https://github.com/dev-k99/MemOS.git
cd MemOS
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure
```bash
cp env.example .env
# Edit .env — fill in GROQ_API_KEY, DATABASE_URL, TAVILY_API_KEY
```

### 3. Initialize Database
```bash
python setup_database.py
```

### 4. Run
```bash
streamlit run app.py
# Opens at http://localhost:8501
```

---

## Deployment

### Streamlit Cloud + Neon (Free)

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io) → New App → Connect repo
3. In **Advanced Settings → Secrets**, add:
```toml
GROQ_API_KEY       = "your_groq_key"
DATABASE_URL       = "postgresql://user:pass@host/db?sslmode=require"
TAVILY_API_KEY     = "tvly-your-key"
LANGCHAIN_API_KEY  = "your_langsmith_key"   # optional
LANGCHAIN_TRACING_V2 = "true"              # optional
LANGCHAIN_PROJECT  = "memos"               # optional
```
4. Deploy — live at `https://your-app-name.streamlit.app`

---

## Free Tier Resource Map

| Resource | Provider | Limit |
|---|---|---|
| LLM inference | Groq | ~14,400 req/day |
| PostgreSQL | Neon | 512 MB |
| Vector store | ChromaDB | Unlimited (local) |
| Embeddings | sentence-transformers | Unlimited (local CPU) |
| Web search | Tavily | 1,000 searches/month |
| Tracing | LangSmith | 5,000 traces/month |
| App hosting | Streamlit Cloud | 1 app, always-on |

**Total: $0.00/month**

---

## Resume Bullet

> Built **MemOS** — an agentic AI assistant with a custom LangGraph `StateGraph`, Tavily web search tool, ChromaDB RAG pipeline, and PostgreSQL cross-session memory — deployed live on Streamlit Cloud with LangSmith observability (zero-cost stack)

---

## Changelog

### v2.0.0 — March 2026
- Custom LangGraph `StateGraph` replacing `create_react_agent` for direct tool binding control
- RAG pipeline: ChromaDB + `all-MiniLM-L6-v2` + PDF/TXT/MD document upload
- Tavily web search (replaced DuckDuckGo — unreliable on cloud deployments)
- LangSmith observability tracing
- Dark theme UI + tool-use indicator chips
- Neon PostgreSQL (replaced Supabase)
- GitHub Pages landing page

### v1.0.0 — February 2026
- Initial release: Streamlit chatbot with PostgreSQL persistent memory

---

<div align="center">
Built with Groq · LangGraph · ChromaDB · PostgreSQL · Streamlit · LangSmith · Tavily
</div>
