"""Chat interface page — conversational AI tutoring."""

import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage

from agents.graph_workflow import mynotebooklm_graph
from config.settings import settings
from ui.components import render_source_cards


def render_chat_page():
    """Render the AI tutor chat interface."""
    st.markdown("### 💬 AI Tutor Chat")
    st.markdown(
        '<p style="color: #94A3B8;">Ask questions about your study materials. '
        "I'll use your knowledge graph, learning history, and uploaded content to help.</p>",
        unsafe_allow_html=True,
    )

    # ── Initialize chat state ────────────────────────────────────────
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []
    if "chat_sources" not in st.session_state:
        st.session_state.chat_sources = {}

    # ── Display chat history ─────────────────────────────────────────
    for i, msg in enumerate(st.session_state.chat_messages):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            # Show sources for assistant messages
            if msg["role"] == "assistant" and i in st.session_state.chat_sources:
                with st.expander("📎 View Sources", expanded=False):
                    render_source_cards(st.session_state.chat_sources[i])

    # ── Chat input ───────────────────────────────────────────────────
    if prompt := st.chat_input("Ask me anything about your study materials..."):
        # Add user message
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("🧠 Thinking..."):
                try:
                    # Build chat history for LangGraph
                    chat_history = []
                    for msg in st.session_state.chat_messages[:-1]:  # exclude current
                        if msg["role"] == "user":
                            chat_history.append(HumanMessage(content=msg["content"]))
                        else:
                            chat_history.append(AIMessage(content=msg["content"]))

                    # Invoke the LangGraph pipeline
                    result = mynotebooklm_graph.invoke({
                        "user_id": settings.app_user_id,
                        "query": prompt,
                        "chat_history": chat_history,
                        "intent": "",
                        "subject_filter": "",
                        "memory_context": "",
                        "retrieved_docs": [],
                        "graph_context": "",
                        "reranked_context": [],
                        "final_answer": "",
                        "sources": [],
                        "quiz_questions": [],
                        "revision_plan": [],
                        "error": "",
                    })

                    answer = result.get("final_answer", "I couldn't generate a response.")
                    sources = result.get("sources", [])

                    st.markdown(answer)

                    # Store and display sources
                    msg_index = len(st.session_state.chat_messages)
                    if sources:
                        st.session_state.chat_sources[msg_index] = sources
                        with st.expander("📎 View Sources", expanded=False):
                            render_source_cards(sources)

                    # Save assistant message
                    st.session_state.chat_messages.append({
                        "role": "assistant",
                        "content": answer,
                    })

                except Exception as e:
                    error_msg = f"⚠️ Error: {e}"
                    st.error(error_msg)
                    st.session_state.chat_messages.append({
                        "role": "assistant",
                        "content": error_msg,
                    })

    # ── Sidebar controls ─────────────────────────────────────────────
    with st.sidebar:
        st.markdown("---")
        if st.button("🗑️ Clear Chat History", use_container_width=True):
            st.session_state.chat_messages = []
            st.session_state.chat_sources = {}
            st.rerun()
