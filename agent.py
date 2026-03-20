"""
MemOS — LangGraph ReAct Agent
Combines persistent PostgreSQL memory, RAG retrieval, and web search.
LangSmith tracing is auto-enabled when LANGCHAIN_API_KEY is set.
"""

import os
import streamlit as st
from typing import Iterator

# ── LangSmith observability (auto-instruments LangChain/LangGraph) ────────────
os.environ.setdefault("LANGCHAIN_TRACING_V2", os.getenv("LANGCHAIN_TRACING_V2", "false"))
os.environ.setdefault("LANGCHAIN_API_KEY", os.getenv("LANGCHAIN_API_KEY", ""))
os.environ.setdefault("LANGCHAIN_PROJECT", os.getenv("LANGCHAIN_PROJECT", "memos"))

from langchain_groq import ChatGroq
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

from tools.search import search_web
from tools.rag_tool import retrieve_from_documents

TOOLS = [search_web, retrieve_from_documents]

SYSTEM_PROMPT = """You are MemOS — an intelligent AI assistant with long-term memory, \
web search, and a personal knowledge base.

Your capabilities:
- You remember every conversation across sessions (stored in PostgreSQL)
- You can search the web for current information using the search_web tool
- You can retrieve information from uploaded documents using retrieve_from_documents
- You think step by step and always cite your sources when using tools

Guidelines:
- Use tools when the question requires current information or document lookup
- Answer directly from memory when you already know the answer
- Be concise but thorough
- When referencing past conversations, explicitly mention that you remember them"""


@st.cache_resource(show_spinner=False)
def build_agent(groq_api_key: str) -> object:
    """Build and cache the LangGraph ReAct agent. Built once per app session."""
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.7,
        groq_api_key=groq_api_key,
        max_tokens=2048,
        streaming=True,
    )
    checkpointer = MemorySaver()
    agent = create_react_agent(
        model=llm,
        tools=TOOLS,
        prompt=SYSTEM_PROMPT,
        checkpointer=checkpointer,
    )
    return agent


def get_pg_history(session_id: str, connection_string: str) -> SQLChatMessageHistory:
    return SQLChatMessageHistory(
        session_id=session_id,
        connection=connection_string,
        table_name="message_store",
    )


def load_pg_messages(session_id: str, connection_string: str) -> list[BaseMessage]:
    """Load stored messages from PostgreSQL to seed the agent's in-memory checkpointer."""
    history = get_pg_history(session_id, connection_string)
    return history.messages


def save_message_to_pg(
    session_id: str, connection_string: str, role: str, content: str
):
    """Persist a single message to PostgreSQL."""
    history = get_pg_history(session_id, connection_string)
    if role == "human":
        history.add_message(HumanMessage(content=content))
    else:
        history.add_message(AIMessage(content=content))


def clear_session(session_id: str, connection_string: str):
    history = get_pg_history(session_id, connection_string)
    history.clear()


def stream_response(
    agent,
    query: str,
    session_id: str,
    connection_string: str,
) -> Iterator[str]:
    """
    Stream the agent's response token by token.
    Yields str chunks suitable for st.write_stream().
    Also persists the exchange to PostgreSQL.
    """
    # Load full PostgreSQL history as seed messages
    pg_messages = load_pg_messages(session_id, connection_string)
    input_messages = pg_messages + [HumanMessage(content=query)]

    config = {"configurable": {"thread_id": session_id}}
    full_response = []

    for chunk in agent.stream(
        {"messages": input_messages},
        config=config,
        stream_mode="messages",
    ):
        # chunk is (message_chunk, metadata) when stream_mode="messages"
        if isinstance(chunk, tuple):
            msg_chunk, meta = chunk
            # Only yield AI text tokens (not tool calls)
            if (
                hasattr(msg_chunk, "content")
                and msg_chunk.content
                and meta.get("langgraph_node") == "agent"
            ):
                text = msg_chunk.content
                full_response.append(text)
                yield text
        else:
            # Fallback: plain string chunk
            if isinstance(chunk, str):
                full_response.append(chunk)
                yield chunk

    # Persist to PostgreSQL after streaming completes
    if full_response:
        save_message_to_pg(session_id, connection_string, "human", query)
        save_message_to_pg(
            session_id, connection_string, "assistant", "".join(full_response)
        )
