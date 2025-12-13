from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # === Paths ===
    PERSIST_DIR: str = "/Users/nemanjaudovic/PycharmProjects/TotallySpies/TotallySpies/backend/src/data"
    CLONING_DIR: str = "/Users/nemanjaudovic/PycharmProjects/TotallySpies/TotallySpies/backend/src/cloning_dir"

    # === Chroma ===
    COLLECTION_NAME: str = "files_vdb"

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

