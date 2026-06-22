"""Document upload page — ingest study materials."""

import streamlit as st
from ingestion.pipeline import ingest_documents
from config.settings import settings
from ui.components import render_stat_badges
import os

UPLOAD_DIR = os.path.join(os.getcwd(), "uploaded_files")
os.makedirs(UPLOAD_DIR, exist_ok=True)


def render_upload_page():
    """Render the document upload and ingestion interface."""
    st.markdown("### 📤 Upload Study Materials")
    st.markdown(
        '<p style="color: #94A3B8;">Upload PDFs, presentations, images of handwritten notes, '
        "or text files. MyNotebookLM will parse, chunk, extract concepts, build a knowledge graph, "
        "and create searchable embeddings.</p>",
        unsafe_allow_html=True,
    )

    # ── Previously Uploaded Files ────────────────────────────────────
    st.markdown("#### 📚 Previously Uploaded Files")
    existing_files = os.listdir(UPLOAD_DIR) if os.path.exists(UPLOAD_DIR) else []
    if existing_files:
        st.markdown(
            f"""
            <div class="glass-card" style="margin-bottom: 1rem;">
                <span style="color: #94A3B8;">
                    {', '.join(existing_files)}
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.info("No files uploaded yet.")

    # ── File uploader ────────────────────────────────────────────────
    uploaded_files = st.file_uploader(
        "Drop your files here",
        type=["pdf", "pptx", "png", "jpg", "jpeg", "tiff", "bmp", "txt", "md"],
        accept_multiple_files=True,
        help="Supports PDF, PPTX, images (OCR), and text files",
    )

    if uploaded_files:
        st.markdown(
            f"""
            <div class="glass-card">
                <strong>📁 {len(uploaded_files)} file(s) selected</strong><br>
                <span style="color: #94A3B8;">
                    {', '.join(f.name for f in uploaded_files)}
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("🚀 Start Ingestion", type="primary", use_container_width=True):
            # Save files to disk and prepare file tuples
            file_tuples = []
            for f in uploaded_files:
                file_path = os.path.join(UPLOAD_DIR, f.name)
                with open(file_path, "wb") as out_f:
                    out_f.write(f.getvalue())
                file_tuples.append((f.name, f.getvalue()))

            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()

            def update_progress(step: str, pct: float):
                progress_bar.progress(pct)
                status_text.markdown(f"**{step}**")

            with st.spinner("Processing..."):
                try:
                    stats = ingest_documents(
                        uploaded_files=file_tuples,
                        user_id=settings.app_user_id,
                        progress_callback=update_progress,
                    )

                    progress_bar.progress(1.0)
                    status_text.markdown("**✅ Ingestion complete!**")

                    # Show results
                    st.success("Documents successfully processed!")
                    st.markdown("---")
                    render_stat_badges({
                        "Files": stats.get("files_processed", 0),
                        "Chunks": stats.get("chunks_created", 0),
                        "Concepts": stats.get("concepts_extracted", 0),
                        "Relationships": stats.get("relationships_created", 0),
                        "Vectors": stats.get("vectors_stored", 0),
                    })

                    # Store in session for reference
                    if "ingestion_history" not in st.session_state:
                        st.session_state.ingestion_history = []
                    st.session_state.ingestion_history.append(stats)

                except Exception as e:
                    st.error(f"❌ Ingestion failed: {e}")
                    progress_bar.progress(0)

    # ── Ingestion history ────────────────────────────────────────────
    if st.session_state.get("ingestion_history"):
        st.markdown("---")
        st.markdown("### 📊 Ingestion History")
        for i, stats in enumerate(reversed(st.session_state.ingestion_history)):
            with st.expander(f"Session {len(st.session_state.ingestion_history) - i}", expanded=False):
                cols = st.columns(5)
                for col, (k, v) in zip(cols, stats.items()):
                    col.metric(k.replace("_", " ").title(), v)
