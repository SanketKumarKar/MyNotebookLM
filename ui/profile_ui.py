"""Learning profile page — memory viewer, strengths, weaknesses."""

import streamlit as st

from memory.mem0_client import MyNotebookMemory
from personalization.weakness_tracker import WeaknessTracker
from config.settings import settings
from ui.components import render_concept_tags


def render_profile_page():
    """Render the user's learning profile and memory viewer."""
    st.markdown("### 🧠 Learning Profile")
    st.markdown(
        '<p style="color: #94A3B8;">Your personalized learning profile built from '
        "all interactions, quiz results, and study patterns.</p>",
        unsafe_allow_html=True,
    )

    try:
        mem = MyNotebookMemory(settings.app_user_id)
        tracker = WeaknessTracker(settings.app_user_id)
    except Exception as e:
        st.error(f"Could not connect to memory: {e}")
        return

    # ── Strengths & Weaknesses ───────────────────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
            <div class="glass-card">
                <h4>💪 Strengths</h4>
            </div>
            """,
            unsafe_allow_html=True,
        )
        strong = tracker.get_strong_concepts()
        if strong:
            render_concept_tags(strong, "strong")
        else:
            st.caption("No strengths recorded yet. Take some quizzes!")

    with col2:
        st.markdown(
            """
            <div class="glass-card">
                <h4>📖 Areas to Improve</h4>
            </div>
            """,
            unsafe_allow_html=True,
        )
        weak = tracker.get_weak_concepts()
        if weak:
            render_concept_tags(weak, "weak")
        else:
            st.caption("No weak areas identified yet. Take some quizzes!")

    # ── Memory Timeline ──────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 🕐 Memory Timeline")

    memories = mem.get_all_memories()
    if memories:
        for i, m in enumerate(reversed(memories[-20:])):  # show last 20
            memory_text = m.get("memory", "") if isinstance(m, dict) else str(m)
            if memory_text:
                # Determine memory type for icon
                if "struggles with" in memory_text:
                    icon = "🔴"
                elif "improved in" in memory_text:
                    icon = "🟢"
                elif "quiz" in memory_text.lower():
                    icon = "📝"
                else:
                    icon = "💭"

                st.markdown(
                    f"""
                    <div class="glass-card" style="padding: 0.8rem 1.2rem;">
                        {icon} {memory_text}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
    else:
        st.info(
            "No memories yet! Start chatting with the AI tutor "
            "or take quizzes to build your learning profile."
        )

    # ── Learning profile summary ─────────────────────────────────────
    st.markdown("---")
    st.markdown("### 📋 Profile Summary")
    profile = mem.get_learning_profile()
    st.markdown(
        f"""
        <div class="glass-card">
            {profile}
        </div>
        """,
        unsafe_allow_html=True,
    )
