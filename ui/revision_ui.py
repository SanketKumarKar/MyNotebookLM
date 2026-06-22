"""Revision schedule page — spaced repetition calendar and export."""

import streamlit as st
import pandas as pd

from agents.graph_workflow import mynotebooklm_graph
from personalization.revision_scheduler import RevisionScheduler
from retrieval.graph_retriever import get_all_subjects
from config.settings import settings
from ui.components import render_stat_badges


def render_revision_page():
    """Render the revision schedule interface."""
    st.markdown("### 📅 Revision Schedule")
    st.markdown(
        '<p style="color: #94A3B8;">Spaced repetition schedule based on your knowledge graph topics. '
        "Review at optimal intervals to maximize retention.</p>",
        unsafe_allow_html=True,
    )

    # ── Generate schedule ────────────────────────────────────────────
    col1, col2 = st.columns([3, 1])
    with col1:
        # Fetch subjects from Neo4j for dropdown
        try:
            subjects = get_all_subjects()
        except Exception:
            subjects = []

        selected_subject = st.selectbox(
            "Focus on subject (optional)",
            options=["All subjects"] + subjects,
        )
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        generate = st.button("📅 Generate Schedule", type="primary", use_container_width=True)

    if generate:
        with st.spinner("Creating revision schedule..."):
            try:
                subject_filter = selected_subject if selected_subject != "All subjects" else ""

                result = mynotebooklm_graph.invoke({
                    "user_id": settings.app_user_id,
                    "query": f"revision plan for {subject_filter}" if subject_filter else "revision plan",
                    "chat_history": [],
                    "intent": "revision",
                    "subject_filter": subject_filter,
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

                plan = result.get("revision_plan", [])
                if plan:
                    st.session_state.revision_plan = plan
                    st.success(f"📅 Created schedule with {len(plan)} revision sessions!")
                else:
                    st.warning("Could not generate a schedule. Upload some materials first!")
            except Exception as e:
                st.error(f"Schedule generation failed: {e}")

    # ── Display schedule ─────────────────────────────────────────────
    if st.session_state.get("revision_plan"):
        plan = st.session_state.revision_plan
        st.markdown("---")

        # Stats
        topics = list(set(s["topic"] for s in plan))
        render_stat_badges({
            "Topics": len(topics),
            "Sessions": len(plan),
            "Days": max(s["interval_days"] for s in plan),
        })

        st.markdown("---")

        # Table view
        df = pd.DataFrame(plan)
        df = df.rename(columns={
            "topic": "📚 Topic",
            "session": "Session #",
            "date": "📅 Date",
            "interval_days": "Days After",
            "priority": "Priority",
        })

        # Color-code priority
        def highlight_priority(val):
            colors = {
                "high": "background-color: rgba(239, 68, 68, 0.2); color: #FCA5A5;",
                "medium": "background-color: rgba(234, 179, 8, 0.2); color: #FDE047;",
                "low": "background-color: rgba(34, 197, 94, 0.2); color: #86EFAC;",
            }
            return colors.get(val, "")

        styled = df.style.applymap(highlight_priority, subset=["Priority"])
        st.dataframe(styled, use_container_width=True, hide_index=True)

        # Export
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            scheduler = RevisionScheduler()
            csv_data = scheduler.export_csv(plan)
            st.download_button(
                "📥 Download CSV",
                data=csv_data,
                file_name="revision_schedule.csv",
                mime="text/csv",
                use_container_width=True,
            )
        with col2:
            if st.button("🗑️ Clear Schedule", use_container_width=True):
                st.session_state.revision_plan = None
                st.rerun()
