# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-02-11

### Added
- Initial release of AI Memory Assistant
- Persistent conversation memory using PostgreSQL
- Groq integration with llama-3.1-8b-instant model
- Streamlit chat interface with real-time updates
- Session-based conversation management
- Memory visualization in sidebar
- Clear memory functionality
- New session creation
- Automated database setup script
- Configuration test suite
- Comprehensive documentation

### Features
- 🧠 **Intelligent Memory**: PostgreSQL-backed persistent storage
- ⚡ **Fast Inference**: Groq's ultra-fast LLM responses
- 💬 **Beautiful UI**: Clean Streamlit chat interface
- 🔒 **Privacy First**: Fully local deployment option
- 🛠️ **Easy Setup**: One-command database initialization
- 📊 **Memory Viewer**: See conversation history in real-time

### Database Schema
- `message_store` table for chat messages
- `sessions` table for session metadata
- Automated triggers for session tracking
- Optimized indexes for fast queries

### Developer Experience
- Environment-based configuration
- Comprehensive test suite
- Clear error messages
- Modular architecture
- Well-documented code

---

## [2.0.0] - 2026-03-21

### Added
- **LangGraph ReAct agent** — replaces simple LangChain chain with stateful graph-based agent
- **RAG pipeline** — ChromaDB + sentence-transformers `all-MiniLM-L6-v2` (local, free)
- **Document upload** — PDF, TXT, MD ingestion via Streamlit file uploader
- **DuckDuckGo web search tool** — no API key required
- **Streaming responses** — token-by-token via Groq streaming + `st.write_stream()`
- **LangSmith tracing** — full observability with 5 lines of config
- **Sample knowledge base** — pre-ingested AI overview + project docs
- **Dark theme UI** — `.streamlit/config.toml` with purple accent
- **GitHub Pages landing page** — `docs/index.html`

### Changed
- Renamed project to **MemOS** — The Memory Operating System for AI
- Upgraded LLM: `llama-3.1-8b-instant` → `llama-3.3-70b-versatile`
- Upgraded all LangChain packages: `0.1.x` → `0.3.x`
- Full README rewrite with Mermaid architecture diagram and badges
- `app.py` refactored for streaming, file upload, agent wiring

---

## Version History

- **2.0.0** (2026-03-21) - Full agentic upgrade — RAG, LangGraph, tools, streaming, LangSmith
- **1.0.0** (2026-02-11) - Initial release

---

[2.0.0]: https://github.com/dev-k99/MemOS/releases/tag/v2.0.0
[1.0.0]: https://github.com/dev-k99/MemOS/releases/tag/v1.0.0