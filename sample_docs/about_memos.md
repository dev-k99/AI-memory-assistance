# About MemOS

## What is MemOS?
MemOS (Memory Operating System) is an agentic AI assistant that combines persistent long-term memory, retrieval-augmented generation (RAG), and real-time web search in a single, deployable application — built entirely on free-tier infrastructure.

## Core Features

### 1. Persistent Long-Term Memory
MemOS stores every conversation in PostgreSQL (hosted on Supabase free tier). Unlike standard chatbots that forget between sessions, MemOS remembers your previous conversations indefinitely.

- Backend: PostgreSQL with JSONB message storage
- ORM: SQLAlchemy 2.0
- History class: SQLChatMessageHistory (LangChain)
- Sessions are identified by UUID and isolated from each other

### 2. RAG — Knowledge Base Search
Users can upload PDF, TXT, or Markdown documents. MemOS chunks, embeds, and stores them in ChromaDB. When a question is relevant, the agent retrieves the top matching chunks and incorporates them into its response.

- Embedding model: sentence-transformers/all-MiniLM-L6-v2 (runs locally, no API key)
- Vector store: ChromaDB (persistent local storage)
- Chunk size: 500 tokens with 50-token overlap
- Retrieval: top-4 similarity search

### 3. Agentic Web Search
MemOS uses a LangGraph ReAct agent that can decide to search the web when it needs current information. Web search uses DuckDuckGo (no API key required).

- Agent framework: LangGraph create_react_agent
- Search tool: DuckDuckGo Search (duckduckgo-search library)
- The agent reasons about which tool to use before acting

### 4. Streaming Responses
Responses stream token-by-token to the UI using Streamlit's st.write_stream() and Groq's streaming API.

### 5. LangSmith Observability
Every agent invocation is traced in LangSmith, showing tool calls, token counts, latency, and the full reasoning trace. Requires a free LangSmith API key.

## Tech Stack

| Layer | Technology | Cost |
|---|---|---|
| Frontend | Streamlit | Free (Streamlit Cloud) |
| LLM | Groq llama-3.3-70b-versatile | Free tier |
| Agent | LangGraph ReAct | Open source |
| Memory | PostgreSQL on Supabase | Free (500MB) |
| Vector DB | ChromaDB | Open source |
| Embeddings | sentence-transformers | Open source (local) |
| Web Search | DuckDuckGo | Free (no key) |
| Observability | LangSmith | Free (5k traces/month) |

**Total monthly cost: $0**

## Architecture
User → Streamlit UI → LangGraph Agent → Tool Router → [DuckDuckGo / ChromaDB RAG / Direct answer] → Groq LLM (streaming) → PostgreSQL (persist)

## Developer
Built by Kwanele as a portfolio project targeting AI Engineer roles. The project demonstrates RAG, agentic tool calling, LLM orchestration, vector databases, streaming, observability, and cloud deployment — all on free infrastructure.

## Version History
- v1.0.0 (Feb 2026): Basic chatbot with PostgreSQL memory
- v2.0.0 (Mar 2026): Full agentic upgrade — RAG, LangGraph, tools, streaming, LangSmith
