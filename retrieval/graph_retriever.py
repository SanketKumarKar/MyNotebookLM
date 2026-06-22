"""Neo4j graph-based retrieval — concept traversal and chunk lookup."""

from langchain_neo4j import Neo4jGraph
from langchain_core.documents import Document
from config.settings import settings
from utils.logger import get_logger

log = get_logger("graph_retriever")

graph = Neo4jGraph(
    url=settings.neo4j_uri,
    username=settings.neo4j_username,
    password=settings.neo4j_password,
)


def get_related_concepts(concept_names: list[str], depth: int = 2) -> list[dict]:
    """Return concepts related to the given names via graph traversal (1-2 hops)."""
    if not concept_names:
        return []
    try:
        result = graph.query(
            """
            MATCH (c:Concept)-[r*1..2]-(related:Concept)
            WHERE c.name IN $names
            RETURN DISTINCT related.name AS concept,
                            related.subject AS subject,
                            related.chapter AS chapter,
                            related.difficulty AS difficulty
            LIMIT 20
            """,
            {"names": concept_names},
        )
        return result
    except Exception as e:
        log.warning(f"Graph concept traversal failed: {e}")
        return []


def get_chunks_by_concepts(concept_names: list[str], limit: int = 10) -> list[Document]:
    """Fetch stored chunk previews linked to given concepts via MENTIONS edges."""
    if not concept_names:
        return []
    try:
        result = graph.query(
            """
            MATCH (ch:Chunk)-[:MENTIONS]->(c:Concept)
            WHERE c.name IN $names
            RETURN DISTINCT ch.text AS text,
                            ch.source_file AS source_file,
                            ch.page_number AS page_number,
                            ch.chunk_index AS chunk_index
            LIMIT $limit
            """,
            {"names": concept_names, "limit": limit},
        )
        docs = []
        for row in result:
            docs.append(
                Document(
                    page_content=row["text"],
                    metadata={
                        "source_file": row["source_file"],
                        "page_number": row["page_number"],
                        "chunk_index": row["chunk_index"],
                        "retrieval_source": "neo4j_graph",
                    },
                )
            )
        return docs
    except Exception as e:
        log.warning(f"Graph chunk retrieval failed: {e}")
        return []


def get_all_subjects() -> list[str]:
    """Return distinct subjects stored in Neo4j (for UI dropdowns)."""
    try:
        result = graph.query("MATCH (c:Concept) RETURN DISTINCT c.subject AS subject")
        return [r["subject"] for r in result if r.get("subject")]
    except Exception as e:
        log.warning(f"Failed to fetch subjects: {e}")
        return []
