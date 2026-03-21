# AI & LLM Concepts Overview

## Large Language Models (LLMs)
Large Language Models are neural networks trained on massive text datasets to predict and generate human-like text. They learn statistical patterns from billions of tokens and can answer questions, write code, summarise documents, and reason through problems.

**Key models in 2025:**
- **Llama 3.3 70B** (Meta, open-weights) — state-of-the-art open model, used by MemOS via Groq
- **GPT-4o** (OpenAI) — strong reasoning and multimodal capability
- **Claude 3.5 Sonnet** (Anthropic) — excels at long-context reasoning and coding
- **Gemini 1.5 Pro** (Google) — 1M token context window

## Retrieval Augmented Generation (RAG)
RAG is a technique that grounds LLM responses in external knowledge, reducing hallucination and enabling answers about private or recent data.

**RAG pipeline:**
1. **Ingest** — Documents are split into chunks (typically 500–1000 tokens)
2. **Embed** — Each chunk is converted to a dense vector using an embedding model (e.g., all-MiniLM-L6-v2)
3. **Store** — Vectors are stored in a vector database (ChromaDB, Pinecone, Weaviate, FAISS)
4. **Retrieve** — At query time, the query is embedded and the top-k most similar chunks are fetched
5. **Generate** — The retrieved chunks are injected into the LLM prompt as context

**Why RAG matters:** It allows AI systems to work with proprietary documents, real-time data, and knowledge beyond the model's training cutoff.

## Agentic AI & Tool Use
Agents are LLMs that can call external tools and take multi-step actions to complete a goal. Instead of a single prompt-response, the model "thinks" iteratively.

**ReAct pattern (Reason + Act):**
1. Model reasons about what to do next
2. Model calls a tool (web search, database, calculator, API)
3. Tool returns a result
4. Model reasons again with new information
5. Repeat until the goal is reached

**Popular agent frameworks:**
- **LangGraph** — stateful, graph-based agents with persistence (used by MemOS)
- **LangChain** — flexible chain-based orchestration
- **AutoGen** — multi-agent conversations
- **CrewAI** — role-based agent crews

## Vector Databases
Vector databases store high-dimensional embeddings and enable semantic similarity search (finding conceptually similar content, not just keyword matches).

**Popular options:**
- **ChromaDB** — open source, local or cloud, great for development (used by MemOS)
- **Pinecone** — fully managed, free tier available
- **Weaviate** — open source with cloud offering
- **FAISS** — Facebook's in-memory library, no persistence

## LangGraph
LangGraph is a framework for building stateful, multi-step AI workflows as directed graphs. Each node in the graph is a function (LLM call, tool call, etc.) and edges define the flow.

**Key concepts:**
- **StateGraph** — the graph that holds conversation state
- **Nodes** — individual processing steps (agent, tool execution)
- **Edges** — conditional routing between nodes
- **Checkpointer** — persists graph state between invocations (MemorySaver, PostgresSaver)
- **create_react_agent** — prebuilt ReAct agent node

## Embeddings
Embeddings are dense numerical vector representations of text. Similar texts produce similar vectors (close in high-dimensional space).

**Common models:**
- `all-MiniLM-L6-v2` — 22MB, fast, 384 dimensions, great for local use (used by MemOS)
- `text-embedding-3-small` — OpenAI, 1536 dimensions
- `nomic-embed-text` — open source, 768 dimensions

## Prompt Engineering
The practice of crafting effective prompts to guide LLM behaviour.

**Techniques:**
- **System prompt** — defines the model's persona, capabilities, and constraints
- **Few-shot examples** — include examples of desired input/output in the prompt
- **Chain of thought** — ask the model to reason step by step before answering
- **Structured output** — request JSON or specific formats using Pydantic
