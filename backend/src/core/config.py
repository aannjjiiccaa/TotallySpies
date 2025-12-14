from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # === Paths === 
    PERSIST_DIR: str = "/Users/marijastakic/Desktop/frontier-hackaton/TotallySpies/backend/src/data"
    CLONING_DIR: str = "/Users/marijastakic/Desktop/frontier-hackaton/TotallySpies/backend/src/cloning_dir"
    JSON_PATH: str = "/Users/marijastakic/Desktop/frontier-hackaton/TotallySpies/backend/graph.json"
    
    # === Chroma ===
    COLLECTION_NAME: str = "files_vdb"

    # === Embeddings ===
    EMBEDDER_MODEL_NAME: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

    # === Groq ===
    GROQ_API_KEY: str
    GROQ_MODEL: str = "openai/gpt-oss-120b"
    TEMPERATURE: float = 0.2

    # === Cohere ===
    COHERE_API_KEY: str
    COHERE_EMBEDDER_MODEL: str = "embed-english-v3.0"
    BATCH_SIZE: int = 3



    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache
def get_settings():
    return Settings()

