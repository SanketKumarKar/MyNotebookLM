"""MyNotebookLM — AI-Powered Personalized Learning System.

Streamlit entry point with sidebar navigation.
"""

import streamlit as st
from ui.components import apply_custom_css, render_header

# ── Page configuration ───────────────────────────────────────────────
st.set_page_config(
    page_title="MyNotebookLM",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Apply premium styling ────────────────────────────────────────────
apply_custom_css()

# ── Sidebar navigation ──────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        """
        <div style="text-align: center; margin-bottom: 2rem;">
            <h2 style="
                background: linear-gradient(135deg, #7C3AED, #2563EB, #06B6D4);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 0;
            ">📚 MyNotebookLM</h2>
            <p style="color: #64748B; font-size: 0.8rem;">AI-Powered Learning</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    page = st.radio(
        "Navigate",
        options=[
            "💬 Chat",
            "📤 Upload Materials",
            "📝 Quiz",
            "🧠 Learning Profile",
            "📅 Revision Schedule",
        ],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown(
        """
        <div style="font-size: 0.75rem; color: #475569; text-align: center;">
            <strong>Powered by</strong><br>
            🦙 Ollama (mistral)<br>
            🧠 Mem0 · 🔷 Qdrant · 🕸️ Neo4j<br>
            🔗 LangGraph · 🦜 LangChain
        </div>
        """,
        unsafe_allow_html=True,
    )

# ── Main content area ────────────────────────────────────────────────
render_header()

if page == "💬 Chat":
    from ui.chat_ui import render_chat_page
    render_chat_page()

elif page == "📤 Upload Materials":
    from ui.upload_ui import render_upload_page
    render_upload_page()

elif page == "📝 Quiz":
    from ui.quiz_ui import render_quiz_page
    render_quiz_page()

elif page == "🧠 Learning Profile":
    from ui.profile_ui import render_profile_page
    render_profile_page()

elif page == "📅 Revision Schedule":
    from ui.revision_ui import render_revision_page
    render_revision_page()
