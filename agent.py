"""
MemOS — LangGraph agent.
Custom graph built with StateGraph/ToolNode so we control the full tool-binding
chain (including parallel_tool_calls=False, which fixes Groq's failed_generation error).
LangSmith tracing is auto-enabled when LANGCHAIN_API_KEY is set before import.
"""

from __future__ import annotations

from typing import Any, Literal

import streamlit as st
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode

from tools.rag_tool import retrieve_from_documents
from tools.search import search_web

TOOLS = [search_web, retrieve_from_documents]

SYSTEM_PROMPT = (
    "You are MemOS — an intelligent AI assistant with long-term memory, "
    "web search, and a personal knowledge base.\n\n"
    "Capabilities:\n"
    "- Every conversation is persisted in PostgreSQL across sessions.\n"
    "- Use search_web for current events, news, or anything outside your training data.\n"
    "- Use retrieve_from_documents for questions about uploaded documents or the knowledge base.\n"
    "- Think step by step and cite sources whenever you use a tool.\n\n"
    "Guidelines:\n"
    "- Prefer answering directly when you already know the answer.\n"
    "- Be concise but thorough.\n"
    "- When referencing past conversations, explicitly say you remember them."
)


def _should_continue(state: MessagesState) -> Literal["tools", "__end__"]:
    last = state["messages"][-1]
    if hasattr(last, "tool_calls") and last.tool_calls:
        return "tools"
    return "__end__"


@st.cache_resource(show_spinner=False)
def build_agent(groq_api_key: str) -> Any:
    """
    Build and cache a custom LangGraph ReAct graph.
    We bind tools directly so we can pass parallel_tool_calls=False,
    which prevents Groq's failed_generation errors on tool calls.
    """
    # streaming=False here prevents Groq from streaming partial tool-call JSON chunks,
    # which can produce malformed function arguments and trigger failed_generation.
    # The graph itself streams tokens to the UI via stream_mode="messages".
    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0.7,
        groq_api_key=groq_api_key,
        max_tokens=2048,
        streaming=False,
    )
    # Bind tools here — we own this call so we can set parallel_tool_calls=False
    llm_with_tools = llm.bind_tools(TOOLS, parallel_tool_calls=False)
    tool_node = ToolNode(TOOLS)

    def agent_node(state: MessagesState) -> dict:
        messages = state["messages"]
        # Inject system prompt if not already present
        if not isinstance(messages[0], SystemMessage):
            messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages
        return {"messages": [llm_with_tools.invoke(messages)]}

    graph = StateGraph(MessagesState)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", tool_node)
    graph.add_edge(START, "agent")
    graph.add_conditional_edges("agent", _should_continue)
    graph.add_edge("tools", "agent")

    # No checkpointer — PostgreSQL is the sole history store.
    # Using MemorySaver alongside PostgreSQL causes duplicate messages in the
    # graph state (checkpoint + loaded history), which breaks tool call formatting.
    return graph.compile()


def get_pg_history(session_id: str, connection_string: str) -> SQLChatMessageHistory:
    return SQLChatMessageHistory(
        session_id=session_id,
        connection=connection_string,
        table_name="message_store",
    )


def load_pg_messages(session_id: str, connection_string: str) -> list[BaseMessage]:
    """Return all stored messages for a session from PostgreSQL."""
    return get_pg_history(session_id, connection_string).messages


def save_message_to_pg(
    session_id: str,
    connection_string: str,
    role: str,
    content: str,
) -> None:
    """Append a single human or assistant message to PostgreSQL."""
    history = get_pg_history(session_id, connection_string)
    msg = HumanMessage(content=content) if role == "human" else AIMessage(content=content)
    history.add_message(msg)


def clear_session(session_id: str, connection_string: str) -> None:
    get_pg_history(session_id, connection_string).clear()


def run_response(
    agent: Any,
    query: str,
    session_id: str,
    connection_string: str,
) -> tuple[str, list[str]]:
    """
    Run the agent and return (response_text, tools_used).
    tools_used contains the names of any tools the agent called (e.g. "search_web").
    Persists the full exchange to PostgreSQL on success.
    """
    input_messages = load_pg_messages(session_id, connection_string) + [
        HumanMessage(content=query)
    ]
    tools_used: list[str] = []
    response_parts: list[str] = []

    for chunk in agent.stream(
        {"messages": input_messages},
        stream_mode="messages",
    ):
        if not isinstance(chunk, tuple):
            continue
        msg_chunk, meta = chunk
        if meta.get("langgraph_node") != "agent":
            continue
        if hasattr(msg_chunk, "tool_calls") and msg_chunk.tool_calls:
            tools_used.extend(tc.get("name", "") for tc in msg_chunk.tool_calls)
        if hasattr(msg_chunk, "content") and msg_chunk.content:
            response_parts.append(msg_chunk.content)

    response_text = "".join(response_parts)
    if response_text:
        save_message_to_pg(session_id, connection_string, "human", query)
        save_message_to_pg(session_id, connection_string, "assistant", response_text)
    return response_text, tools_used
