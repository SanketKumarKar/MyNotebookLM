"""Semantic chunking with fallback to recursive character splitting."""

from langchain_experimental.text_splitter import SemanticChunker
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from utils.llm import embeddings
from utils.logger import get_logger

log = get_logger("chunker")

# Primary: semantic chunker driven by embedding similarity
_semantic_chunker = SemanticChunker(
    embeddings=embeddings,
    breakpoint_threshold_type="percentile",
    breakpoint_threshold_amount=95,
)

# Fallback: for chunks that exceed token budget
_fallback_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=300,
    separators=["\n\n", "\n", ". ", " ", ""],
)

MAX_CHUNK_CHARS = 6000  # ~1500 tokens ≈ 6000 chars


def chunk_documents(docs: list[Document]) -> list[Document]:
    """
    Semantically chunk a list of Documents.

    Steps:
        1. Run SemanticChunker on each document
        2. For any resulting chunk > MAX_CHUNK_CHARS, re-split with RecursiveCharacterTextSplitter
        3. Assign chunk_index to each chunk's metadata
    """
    all_chunks: list[Document] = []
    chunk_index = 0

    for doc in docs:
        if not doc.page_content.strip():
            continue

        try:
            semantic_chunks = _semantic_chunker.create_documents(
                [doc.page_content],
                metadatas=[doc.metadata],
            )
        except Exception as e:
            log.warning(f"Semantic chunking failed, using fallback: {e}")
            semantic_chunks = _fallback_splitter.create_documents(
                [doc.page_content],
                metadatas=[doc.metadata],
            )

        for chunk in semantic_chunks:
            # Re-split oversized chunks
            if len(chunk.page_content) > MAX_CHUNK_CHARS:
                sub_chunks = _fallback_splitter.create_documents(
                    [chunk.page_content],
                    metadatas=[chunk.metadata],
                )
                for sc in sub_chunks:
                    sc.metadata = {**doc.metadata, **sc.metadata, "chunk_index": chunk_index}
                    all_chunks.append(sc)
                    chunk_index += 1
            else:
                chunk.metadata = {**doc.metadata, **chunk.metadata, "chunk_index": chunk_index}
                all_chunks.append(chunk)
                chunk_index += 1

    log.info(f"Chunking complete: {len(docs)} docs → {len(all_chunks)} chunks")
    return all_chunks
