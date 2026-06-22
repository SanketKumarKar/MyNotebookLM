"""Neo4j knowledge graph builder — upsert concepts, relationships, and chunk nodes."""

from langchain_neo4j import Neo4jGraph
from config.settings import settings
from utils.logger import get_logger

log = get_logger("graph_builder")

graph = Neo4jGraph(
    url=settings.neo4j_uri,
    username=settings.neo4j_username,
    password=settings.neo4j_password,
)

_VALID_REL_TYPES = {
    "DEPENDS_ON", "IS_A", "PART_OF", "RELATED_TO",
    "PREREQUISITE_OF", "EXAMPLE_OF", "CONTRASTS_WITH",
}


def init_constraints():
    """Create indexes and constraints on first run."""
    try:
        graph.query("CREATE INDEX concept_name IF NOT EXISTS FOR (c:Concept) ON (c.name)")
        graph.query("CREATE INDEX chunk_id IF NOT EXISTS FOR (ch:Chunk) ON (ch.id)")
        log.info("Neo4j indexes ensured")
    except Exception as e:
        log.warning(f"Index creation issue (may already exist): {e}")


def upsert_concept(name: str, subject: str, chapter: str, difficulty: str):
    """Merge a Concept node (create-or-update)."""
    graph.query(
        """
        MERGE (c:Concept {name: $name})
        ON CREATE SET c.subject = $subject, c.chapter = $chapter, c.difficulty = $difficulty
        ON MATCH SET c.subject = $subject, c.chapter = $chapter
        """,
        {"name": name, "subject": subject, "chapter": chapter, "difficulty": difficulty},
    )


def upsert_relationship(from_concept: str, rel_type: str, to_concept: str):
    """Merge a typed relationship between two Concept nodes."""
    if rel_type not in _VALID_REL_TYPES:
        rel_type = "RELATED_TO"
    query = f"""
        MERGE (a:Concept {{name: $from_name}})
        MERGE (b:Concept {{name: $to_name}})
        MERGE (a)-[:{rel_type}]->(b)
    """
    graph.query(query, {"from_name": from_concept, "to_name": to_concept})


def upsert_chunk(chunk_id: str, text: str, source_file: str, page_number: int, chunk_index: int):
    """Merge a Chunk node with preview text."""
    graph.query(
        """
        MERGE (ch:Chunk {id: $id})
        ON CREATE SET ch.text = $text, ch.source_file = $source_file,
                      ch.page_number = $page_number, ch.chunk_index = $chunk_index
        """,
        {
            "id": chunk_id,
            "text": text,
            "source_file": source_file,
            "page_number": page_number,
            "chunk_index": chunk_index,
        },
    )


def link_chunk_to_concepts(chunk_id: str, concept_names: list[str]):
    """Create MENTIONS edges from a Chunk to its Concepts."""
    for name in concept_names:
        graph.query(
            """
            MATCH (ch:Chunk {id: $chunk_id})
            MERGE (c:Concept {name: $concept_name})
            MERGE (ch)-[:MENTIONS]->(c)
            """,
            {"chunk_id": chunk_id, "concept_name": name},
        )


def build_graph_from_extraction(chunks, extraction_results: list[dict]):
    """
    Populate the Neo4j graph from entity extraction results.
    Also back-fills metadata onto chunk objects for downstream Qdrant storage.
    """
    init_constraints()

    for chunk, extraction in zip(chunks, extraction_results):
        subject = extraction.get("subject", "General")
        chapter = extraction.get("chapter", "General")
        difficulty = extraction.get("difficulty", "intermediate")
        concepts = extraction.get("concepts", [])
        relationships = extraction.get("relationships", [])

        # Upsert concept nodes
        for concept in concepts:
            upsert_concept(concept, subject, chapter, difficulty)

        # Upsert relationship edges
        for rel in relationships:
            try:
                upsert_relationship(rel["from"], rel["type"], rel["to"])
            except (KeyError, TypeError) as e:
                log.warning(f"Skipping malformed relationship: {rel} — {e}")

        # Upsert chunk node and link to concepts
        chunk_id = f"{chunk.metadata.get('source_file', 'unknown')}__chunk_{chunk.metadata.get('chunk_index', 0)}"
        upsert_chunk(
            chunk_id=chunk_id,
            text=chunk.page_content[:500],  # store preview, not full text
            source_file=chunk.metadata.get("source_file", "unknown"),
            page_number=chunk.metadata.get("page_number", 0),
            chunk_index=chunk.metadata.get("chunk_index", 0),
        )
        link_chunk_to_concepts(chunk_id, concepts)

        # Back-fill metadata onto chunk for Qdrant
        chunk.metadata["subject"] = subject
        chunk.metadata["chapter"] = chapter
        chunk.metadata["difficulty"] = difficulty
        chunk.metadata["chunk_id"] = chunk_id

    total_concepts = sum(len(e.get("concepts", [])) for e in extraction_results)
    total_rels = sum(len(e.get("relationships", [])) for e in extraction_results)
    log.info(f"Graph built: {total_concepts} concepts, {total_rels} relationships")
