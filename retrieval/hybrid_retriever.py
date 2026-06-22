"""Hybrid retriever: RRF fusion of vector + BM25 + graph, then cross-encoder reranking."""

from langchain_core.documents import Document
from retrieval.vector_retriever import retrieve as vector_retrieve
from retrieval.bm25_retriever import bm25_search
from retrieval.graph_retriever import get_chunks_by_concepts
from retrieval.reranker import rerank
from ingestion.entity_extractor import extract_entities
from utils.logger import get_logger

log = get_logger("hybrid_retriever")

RRF_K = 60  # standard Reciprocal Rank Fusion constant


def reciprocal_rank_fusion(result_lists: list[list[Document]]) -> list[Document]:
    """
    Fuse multiple ranked lists using Reciprocal Rank Fusion (RRF).
    Deduplicates by page_content hash.
    """
    scores: dict[str, float] = {}
    doc_map: dict[str, Document] = {}

    for result_list in result_lists:
        for rank, doc in enumerate(result_list):
            key = str(hash(doc.page_content[:200]))
            if key not in doc_map:
                doc_map[key] = doc
                scores[key] = 0.0
            scores[key] += 1.0 / (RRF_K + rank + 1)

    sorted_keys = sorted(scores, key=lambda k: scores[k], reverse=True)
    return [doc_map[k] for k in sorted_keys]


def hybrid_retrieve(
    query: str, k_final: int = 5, subject_filter: str | None = None
) -> list[Document]:
    """
    Full retrieval pipeline:
      1. Dense vector search via Qdrant
      2. BM25 keyword search via rank-bm25
      3. Neo4j graph chunk retrieval (concept-based)
      4. RRF fusion
      5. BGE cross-encoder reranking → top k_final
    """
    # 1. Vector search
    try:
        vector_results = vector_retrieve(query, k=15, subject_filter=subject_filter)
    except Exception as e:
        log.warning(f"Vector retrieval failed: {e}")
        vector_results = []

    # 2. BM25
    try:
        bm25_results = bm25_search(query, k=15)
    except Exception as e:
        log.warning(f"BM25 retrieval failed: {e}")
        bm25_results = []

    # 3. Graph retrieval — extract concept names from query first
    graph_results = []
    try:
        extraction = extract_entities(query)
        concept_names = extraction.get("concepts", [])
        if concept_names:
            graph_results = get_chunks_by_concepts(concept_names, limit=10)
    except Exception as e:
        log.warning(f"Graph retrieval failed: {e}")

    # 4. RRF fusion
    fused = reciprocal_rank_fusion([vector_results, bm25_results, graph_results])
    log.info(
        f"Fusion: {len(vector_results)} vector + {len(bm25_results)} BM25 + "
        f"{len(graph_results)} graph → {len(fused)} fused"
    )

    # 5. Cross-encoder rerank → top k_final
    if fused:
        reranked = rerank(query, fused[:20], top_k=k_final)
    else:
        reranked = []

    return reranked
