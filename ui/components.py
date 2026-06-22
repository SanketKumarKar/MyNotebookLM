"""Reusable Streamlit UI components for MyNotebookLM."""

import streamlit as st


def apply_custom_css():
    """Inject custom CSS for a premium dark-themed learning platform."""
    st.markdown("""
    <style>
    /* ── Import Google Font ─────────────────────────────────────────── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    * { font-family: 'Inter', sans-serif; }

    /* ── Gradient header bar ────────────────────────────────────────── */
    .main-header {
        background: linear-gradient(135deg, #7C3AED 0%, #2563EB 50%, #06B6D4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        color: #94A3B8;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }

    /* ── Glassmorphism cards ────────────────────────────────────────── */
    .glass-card {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(148, 163, 184, 0.15);
        border-radius: 16px;
        padding: 1.5rem;
        backdrop-filter: blur(12px);
        margin-bottom: 1rem;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .glass-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 32px rgba(124, 58, 237, 0.15);
    }

    /* ── Source citation cards ──────────────────────────────────────── */
    .source-card {
        background: rgba(30, 41, 59, 0.5);
        border-left: 3px solid #7C3AED;
        border-radius: 0 12px 12px 0;
        padding: 0.8rem 1.2rem;
        margin: 0.5rem 0;
        font-size: 0.85rem;
    }
    .source-card .source-file {
        color: #A78BFA;
        font-weight: 600;
    }
    .source-card .source-preview {
        color: #94A3B8;
        font-size: 0.8rem;
        margin-top: 0.3rem;
    }

    /* ── Stat badges ───────────────────────────────────────────────── */
    .stat-badge {
        display: inline-block;
        background: linear-gradient(135deg, #7C3AED20, #2563EB20);
        border: 1px solid #7C3AED40;
        border-radius: 12px;
        padding: 0.6rem 1.2rem;
        text-align: center;
        min-width: 120px;
    }
    .stat-badge .stat-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #A78BFA;
    }
    .stat-badge .stat-label {
        font-size: 0.75rem;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* ── Quiz styling ──────────────────────────────────────────────── */
    .quiz-correct {
        background: rgba(34, 197, 94, 0.1);
        border: 1px solid rgba(34, 197, 94, 0.3);
        border-radius: 12px;
        padding: 1rem;
    }
    .quiz-incorrect {
        background: rgba(239, 68, 68, 0.1);
        border: 1px solid rgba(239, 68, 68, 0.3);
        border-radius: 12px;
        padding: 1rem;
    }

    /* ── Concept tags ──────────────────────────────────────────────── */
    .concept-tag {
        display: inline-block;
        background: #7C3AED20;
        color: #A78BFA;
        border-radius: 999px;
        padding: 0.3rem 0.8rem;
        font-size: 0.8rem;
        margin: 0.2rem;
        font-weight: 500;
    }
    .concept-tag-weak {
        background: #EF444420;
        color: #FCA5A5;
    }
    .concept-tag-strong {
        background: #22C55E20;
        color: #86EFAC;
    }

    /* ── Progress bar enhancement ──────────────────────────────────── */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #7C3AED, #2563EB, #06B6D4);
    }

    /* ── Sidebar styling ───────────────────────────────────────────── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0F172A 0%, #1E293B 100%);
    }

    /* ── Chat message styling ──────────────────────────────────────── */
    .stChatMessage {
        border-radius: 16px !important;
    }

    /* ── Hide Streamlit branding ───────────────────────────────────── */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)


def render_header():
    """Render the main app header."""
    st.markdown('<h1 class="main-header">📚 MyNotebookLM</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">AI-Powered Personalized Learning System — '
        'Knowledge Graph · Adaptive Memory · Intelligent Tutoring</p>',
        unsafe_allow_html=True,
    )


def render_stat_badges(stats: dict):
    """Render a row of statistic badges."""
    cols = st.columns(len(stats))
    for col, (label, value) in zip(cols, stats.items()):
        with col:
            st.markdown(
                f"""
                <div class="stat-badge">
                    <div class="stat-value">{value}</div>
                    <div class="stat-label">{label}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_source_cards(sources: list[dict]):
    """Render source citation cards."""
    if not sources:
        return
    st.markdown("**📎 Sources**")
    for src in sources:
        st.markdown(
            f"""
            <div class="source-card">
                <div class="source-file">📄 {src.get('file', 'Unknown')} — Page {src.get('page', '?')}</div>
                <div class="source-preview">{src.get('preview', '')}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_concept_tags(concepts: list[str], tag_type: str = "default"):
    """Render concept tags (default, weak, or strong)."""
    css_class = {
        "weak": "concept-tag concept-tag-weak",
        "strong": "concept-tag concept-tag-strong",
    }.get(tag_type, "concept-tag")

    tags_html = "".join(f'<span class="{css_class}">{c}</span>' for c in concepts)
    st.markdown(tags_html, unsafe_allow_html=True)
