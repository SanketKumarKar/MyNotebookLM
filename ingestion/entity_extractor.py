"""LLM-based entity & concept extraction from text chunks."""

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from utils.llm import llm
from utils.logger import get_logger

log = get_logger("entity_extractor")

_extraction_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a knowledge graph builder for an educational AI tutor.
Given a text chunk from study material, extract the following.
Return ONLY valid JSON, no preamble, no markdown fences.

Schema:
{{
    "concepts": ["concept1", "concept2"],
    "relationships": [
        {{"from": "concept1", "type": "DEPENDS_ON", "to": "concept2"}}
    ],
    "subject": "subject name",
    "chapter": "chapter or topic name",
    "difficulty": "beginner|intermediate|advanced"
}}

Valid relationship types: DEPENDS_ON, IS_A, PART_OF, RELATED_TO, PREREQUISITE_OF, EXAMPLE_OF, CONTRASTS_WITH

Rules:
- concepts must be important named terms, algorithms, theorems, or definitions
- difficulty must be exactly one of: beginner, intermediate, advanced
- Return at least 1 concept per chunk
- If you cannot determine subject or chapter, use "General"
"""),
    ("human", "Text chunk:\n{chunk_text}")
])

_extraction_chain = _extraction_prompt | llm | JsonOutputParser()


def extract_entities(chunk_text: str) -> dict:
    """
    Extract concepts, relationships, subject, chapter, difficulty from a text chunk.

    Returns:
        {
            "concepts": [...],
            "relationships": [...],
            "subject": "...",
            "chapter": "...",
            "difficulty": "..."
        }
    On parse failure, returns safe defaults.
    """
    try:
        result = _extraction_chain.invoke({"chunk_text": chunk_text[:3000]})
        # Validate required keys
        result.setdefault("concepts", [])
        result.setdefault("relationships", [])
        result.setdefault("subject", "General")
        result.setdefault("chapter", "General")
        result.setdefault("difficulty", "intermediate")
        return result
    except Exception as e:
        log.warning(f"Entity extraction failed: {e}")
        return {
            "concepts": [],
            "relationships": [],
            "subject": "General",
            "chapter": "General",
            "difficulty": "intermediate",
        }


def batch_extract(chunks, batch_size: int = 5) -> list[dict]:
    """Process chunks in small batches to avoid overloading local Ollama."""
    results = []
    total = len(chunks)
    for i in range(0, total, batch_size):
        batch = chunks[i : i + batch_size]
        for j, chunk in enumerate(batch):
            log.debug(f"Extracting entities from chunk {i + j + 1}/{total}")
            result = extract_entities(chunk.page_content)
            results.append(result)
    log.info(f"Entity extraction complete: {total} chunks processed")
    return results
