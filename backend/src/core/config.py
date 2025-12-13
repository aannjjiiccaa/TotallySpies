from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # === Paths ===
    PERSIST_DIR: str = "/Users/nemanjaudovic/PycharmProjects/bar_review/where/ai_api/app/data/bars_db"
    ENTRIES_DIR: str = "/Users/nemanjaudovic/PycharmProjects/bar_review/where/ai_api/app/data/raw"

    # === Chroma ===
    COLLECTION_NAME: str = "reviews_vdb"

    # === Embeddings ===
    EMBEDDER_MODEL_NAME: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

    # === RAG ===
    CHUNK_SIZE: int = 20
    RETRIEVER_K: int = 5

    # === Groq ===
    GROQ_API_KEY: str
    GROQ_MODEL: str = "openai/gpt-oss-20b"
    TEMPERATURE: float = 0.5

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache
def get_settings():
    return Settings()

