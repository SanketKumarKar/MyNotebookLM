"""Full ingestion pipeline: parse → chunk → extract → graph → vectorize → BM25."""

import tempfile
import os

from ingestion.document_loader import load_document
from ingestion.chunker import chunk_documents
from ingestion.entity_extractor import batch_extract
from ingestion.graph_builder import build_graph_from_extraction
from ingestion.vector_store import add_documents
from utils.logger import get_logger

log = get_logger("ingestion_pipeline")


def ingest_documents(uploaded_files: list, user_id: str, progress_callback=None) -> dict:
    """
    Full ingestion orchestrator.

    Args:
        uploaded_files: list of (filename, bytes) tuples from Streamlit uploader
        user_id: current user ID
        progress_callback: optional callable(step: str, pct: float)

    Returns:
        dict with ingestion statistics
    """

    def progress(step: str, pct: float):
        if progress_callback:
            progress_callback(step, pct)

    all_docs = []

    # ── Step 1: Parse documents ──────────────────────────────────────
    progress("📄 Parsing documents...", 0.10)
    with tempfile.TemporaryDirectory() as tmpdir:
        for filename, file_bytes in uploaded_files:
            tmp_path = os.path.join(tmpdir, filename)
            with open(tmp_path, "wb") as f:
                f.write(file_bytes)
            docs = load_document(tmp_path, filename)
            all_docs.extend(docs)

    if not all_docs:
        log.warning("No content extracted from uploaded files")
        return {
            "files_processed": len(uploaded_files),
            "chunks_created": 0,
            "concepts_extracted": 0,
            "relationships_created": 0,
            "vectors_stored": 0,
        }

    # ── Step 2: Semantic chunking ────────────────────────────────────
    progress("✂️ Chunking content...", 0.25)
    chunks = chunk_documents(all_docs)

    # ── Step 3: Entity extraction via Ollama ─────────────────────────
    progress("🔍 Extracting concepts via Ollama (mistral)...", 0.40)
    extraction_results = batch_extract(chunks)

    # ── Step 4: Build Neo4j knowledge graph ──────────────────────────
    progress("🕸️ Building knowledge graph...", 0.60)
    build_graph_from_extraction(chunks, extraction_results)

    # ── Step 5: Store vectors in Qdrant ──────────────────────────────
    progress("💾 Storing embeddings in Qdrant...", 0.80)
    add_documents(chunks)

    # ── Step 6: Rebuild BM25 index ───────────────────────────────────
    progress("🔁 Rebuilding BM25 index...", 0.90)
    try:
        from retrieval.bm25_retriever import rebuild_bm25_index
        rebuild_bm25_index()
    except Exception as e:
        log.warning(f"BM25 index rebuild failed (non-critical): {e}")

    progress("✅ Done!", 1.0)

    total_concepts = sum(len(e.get("concepts", [])) for e in extraction_results)
    total_rels = sum(len(e.get("relationships", [])) for e in extraction_results)

    stats = {
        "files_processed": len(uploaded_files),
        "chunks_created": len(chunks),
        "concepts_extracted": total_concepts,
        "relationships_created": total_rels,
        "vectors_stored": len(chunks),
    }
    log.info(f"Ingestion complete: {stats}")
    return stats
