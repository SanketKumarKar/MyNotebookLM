"""Quiz page — interactive quizzes with grading and weakness tracking."""

import streamlit as st
from langchain_core.messages import HumanMessage

from agents.graph_workflow import mynotebooklm_graph
from personalization.quiz_engine import QuizEngine
from config.settings import settings
from ui.components import render_concept_tags


def render_quiz_page():
    """Render the interactive quiz interface."""
    st.markdown("### 📝 Quiz Yourself")
    st.markdown(
        '<p style="color: #94A3B8;">Test your understanding with AI-generated quizzes. '
        "Results are tracked to identify your weak spots.</p>",
        unsafe_allow_html=True,
    )

    # ── Initialize quiz state ────────────────────────────────────────
    if "quiz_session" not in st.session_state:
        st.session_state.quiz_session = None
    if "quiz_engine" not in st.session_state:
        st.session_state.quiz_engine = QuizEngine(settings.app_user_id)

    # ── Generate quiz ────────────────────────────────────────────────
    if st.session_state.quiz_session is None:
        col1, col2 = st.columns([3, 1])
        with col1:
            topic = st.text_input(
                "📚 Topic (optional)",
                placeholder="Leave blank for all topics, or enter a subject...",
            )
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            generate = st.button("🎯 Generate Quiz", type="primary", use_container_width=True)

        if generate:
            with st.spinner("🧠 Generating quiz questions..."):
                try:
                    result = mynotebooklm_graph.invoke({
                        "user_id": settings.app_user_id,
                        "query": f"quiz me on {topic}" if topic else "quiz me on everything",
                        "chat_history": [],
                        "intent": "quiz",
                        "subject_filter": topic,
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

                    questions = result.get("quiz_questions", [])
                    if questions:
                        engine = st.session_state.quiz_engine
                        st.session_state.quiz_session = engine.start_session(questions)
                        st.rerun()
                    else:
                        st.warning("No questions could be generated. Upload some materials first!")
                except Exception as e:
                    st.error(f"Quiz generation failed: {e}")
    else:
        # ── Active quiz session ──────────────────────────────────────
        session = st.session_state.quiz_session
        engine = st.session_state.quiz_engine

        # Progress
        answered = session.answered
        total = session.total
        st.progress(answered / max(total, 1))
        st.markdown(
            f"**Question {answered + 1} of {total}** "
            f"({'✓ ' + str(session.score) + ' correct' if answered > 0 else ''})"
        )

        # Show current question
        if answered < total:
            q = session.questions[answered]
            q_type = q.get("type", "mcq")
            concept = q.get("concept", "")
            difficulty = q.get("difficulty", "")

            st.markdown(
                f"""
                <div class="glass-card">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.8rem;">
                        <span class="concept-tag">{concept}</span>
                        <span style="color: #94A3B8; font-size: 0.8rem;">
                            {'🟢' if difficulty == 'beginner' else '🟡' if difficulty == 'intermediate' else '🔴'}
                            {difficulty}
                        </span>
                    </div>
                    <h4>{q['question']}</h4>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if q_type == "mcq":
                options = q.get("options", [])
                answer = st.radio(
                    "Select your answer:",
                    options,
                    key=f"quiz_q_{answered}",
                    label_visibility="collapsed",
                )
                if st.button("Submit Answer", key=f"submit_{answered}"):
                    _process_answer(session, engine, answered, answer)

            elif q_type == "short_answer":
                answer = st.text_area(
                    "Your answer:",
                    key=f"quiz_sa_{answered}",
                    height=100,
                )
                if st.button("Submit Answer", key=f"submit_{answered}"):
                    if answer.strip():
                        _process_answer(session, engine, answered, answer)
                    else:
                        st.warning("Please enter an answer.")
        else:
            # Quiz complete
            _show_results(session, engine)

        # Reset button
        st.markdown("---")
        if st.button("🔄 New Quiz", use_container_width=True):
            st.session_state.quiz_session = None
            st.rerun()


def _process_answer(session, engine, q_index, answer):
    """Grade an answer and show feedback."""
    result = engine.submit_answer(session, q_index, answer)
    if result["correct"]:
        st.markdown(
            f"""
            <div class="quiz-correct">
                ✅ <strong>Correct!</strong><br>
                <span style="color: #94A3B8;">{result.get('explanation', '')}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <div class="quiz-incorrect">
                ❌ <strong>Incorrect.</strong> The correct answer is: <strong>{result['correct_answer']}</strong><br>
                <span style="color: #94A3B8;">{result.get('explanation', '')}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    import time
    time.sleep(1.5)
    st.rerun()


def _show_results(session, engine):
    """Show quiz results summary."""
    summary = engine.finalize_session(session)
    pct = summary["percentage"]
    emoji = "🏆" if pct >= 80 else "👍" if pct >= 60 else "📖"

    st.markdown(
        f"""
        <div class="glass-card" style="text-align: center;">
            <h2>{emoji} Quiz Complete!</h2>
            <div class="stat-value" style="font-size: 3rem; color: {'#22C55E' if pct >= 60 else '#EF4444'};">
                {pct}%
            </div>
            <p style="color: #94A3B8;">
                {summary['correct']}/{summary['total']} correct
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    weak = summary.get("weak_concepts", [])
    if weak:
        st.markdown("**Concepts to review:**")
        render_concept_tags(weak, "weak")
