"""
AI Assistant with Long-Term Memory
Built with Groq, PostgreSQL, and Streamlit
"""

import streamlit as st
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
import uuid
from datetime import datetime

# Load environment variables (for local development)
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
# ================== Configuration ==================

def get_config():
    """
    Get configuration from Streamlit secrets (production) or .env (local)
    Priority: st.secrets > environment variables
    """
    config = {}
    
    # Try to get from Streamlit secrets first (production deployment)
    try:
        config['groq_api_key'] = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY"))
        config['database_url'] = st.secrets.get("DATABASE_URL", os.getenv("DATABASE_URL"))
    except Exception:
        # Fall back to environment variables (local development)
        config['groq_api_key'] = os.getenv("GROQ_API_KEY")
        config['database_url'] = os.getenv("DATABASE_URL")
    
    return config

# ================== Database Setup ==================

def get_session_history(session_id: str, connection_string: str):
    """
    Create or retrieve PostgreSQL chat message history for a session.
    """

    return SQLChatMessageHistory(
        session_id=session_id,
        connection=connection_string,   #  new API (not deprecated)
        table_name="message_store",
    )


def clear_session_memory(session_id: str, connection_string: str):
    """
    Clear all messages for a specific session
    """
    history = get_session_history(session_id, connection_string)
    history.clear()

# ================== LLM Setup ==================

def create_llm_chain(groq_api_key: str, connection_string: str):
    """
    Create a LangChain chain with Groq LLM and PostgreSQL memory
    """
    # Initialize Groq LLM
    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0.7,
        groq_api_key=groq_api_key,
        max_tokens=1024
    )
    
    # Create prompt template with message history
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful AI assistant with long-term memory. "
                   "You remember previous conversations and can reference them. "
                   "Be conversational, helpful, and maintain context across sessions."),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}")
    ])
    
    # Create the chain
    chain = prompt | llm
    
    # Wrap with message history
    chain_with_history = RunnableWithMessageHistory(
        chain,
        lambda session_id: get_session_history(session_id, connection_string),
        input_messages_key="input",
        history_messages_key="history"
    )
    
    return chain_with_history

# ================== Streamlit UI ==================

def main():
    st.set_page_config(
        page_title="AI Assistant with Memory",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("AI Assistant with Long-Term Memory")
    st.caption("Powered by Groq (Llama 3.1 8B) and PostgreSQL")
    
    # Load configuration
    config = get_config()
    
    # Check if configuration is complete
    if not config.get('groq_api_key') or not config.get('database_url'):
        st.error("Missing Configuration")
        st.info(
            "Please set up your environment:\n\n"
            "**Local Development:**\n"
            "1. Copy `.env.example` to `.env`\n"
            "2. Add your `GROQ_API_KEY` and `DATABASE_URL`\n\n"
            "**Production (Streamlit Cloud):**\n"
            "1. Go to App Settings → Secrets\n"
            "2. Add `GROQ_API_KEY` and `DATABASE_URL`"
        )
        st.stop()
    
    # Initialize session state
    if 'session_id' not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # ================== Sidebar ==================
    with st.sidebar:
        st.header("Session Management")
        
        # Display current session ID
        st.info(f"**Session ID:**\n`{st.session_state.session_id[:8]}...`")
        
        # Database status
        try:
            history = get_session_history(
                st.session_state.session_id,
                config['database_url']
            )
            stored_messages = history.messages
            st.success(f"Database Connected")
            st.metric("Messages in Memory", len(stored_messages))
        except Exception as e:
            st.error(f"Database Error: {str(e)}")
            stored_messages = []
        
        st.divider()
        
        # Memory Display
        st.subheader("Current Session Memory")
        
        if stored_messages:
            with st.expander("View All Messages", expanded=False):
                for i, msg in enumerate(stored_messages):
                    role = "User" if isinstance(msg, HumanMessage) else "Assistant"
                    st.text(f"{role}:")
                    st.caption(msg.content[:100] + "..." if len(msg.content) > 100 else msg.content)
                    if i < len(stored_messages) - 1:
                        st.divider()
        else:
            st.info("No messages yet. Start a conversation!")
        
        st.divider()
        
        # Clear Memory Button
        if st.button("Clear Memory", type="secondary", use_container_width=True):
            try:
                clear_session_memory(st.session_state.session_id, config['database_url'])
                st.session_state.messages = []
                st.success("Memory cleared!")
                st.rerun()
            except Exception as e:
                st.error(f"Error clearing memory: {str(e)}")
        
        # New Session Button
        if st.button("New Session", type="primary", use_container_width=True):
            st.session_state.session_id = str(uuid.uuid4())
            st.session_state.messages = []
            st.success("New session started!")
            st.rerun()
        
        st.divider()
        
        # Settings
        with st.expander("Settings"):
            st.caption("**Model:** llama-3.1-8b-instant")
            st.caption("**Database:** PostgreSQL")
            st.caption(f"**Environment:** {'Production' if 'STREAMLIT' in os.environ else 'Local'}")
    
    # ================== Main Chat Interface ==================
    
    # Load chat history from session state
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask me anything..."):
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Add to session state
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    # Create LLM chain
                    chain_with_history = create_llm_chain(
                        config['groq_api_key'],
                        config['database_url']
                    )
                    
                    # Get response with history context
                    response = chain_with_history.invoke(
                        {"input": prompt},
                        config={"configurable": {"session_id": st.session_state.session_id}}
                    )
                    
                    # Extract content
                    response_content = response.content
                    
                    # Display response
                    st.markdown(response_content)
                    
                    # Add to session state
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response_content
                    })
                    
                except Exception as e:
                    error_msg = f"Error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })
    
    # Footer
    st.divider()
    st.caption(
        "**Tip:** This assistant remembers your conversation history. "
        "Try asking it to recall something from earlier in the conversation!"
    )

if __name__ == "__main__":
    main()