from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Central configuration loaded from environment variables / .env file."""

    # Ollama (running on host, accessed via host.docker.internal)
    ollama_base_url: str = "http://host.docker.internal:11434"
    ollama_llm_model: str = "mistral"
    ollama_embedding_model: str = "qwen3-embedding:4b"
    embedding_dimensions: int = 2560  # qwen3-embedding:4b output dim

    # Qdrant
    qdrant_url: str = "http://qdrant:6333"
    qdrant_api_key: str = ""
    qdrant_collection: str = "mynotebooklm_docs"

    # Neo4j
    neo4j_uri: str = "bolt://neo4j:7687"
    neo4j_username: str = "neo4j"
    neo4j_password: str = "mynotebooklm123"

    # Mem0 Cloud API
    mem0_api_key: str = ""

    # Mistral Cloud API (for LLM)
    mistral_api_key: str = ""

    # App
    app_user_id: str = "default_user"
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
