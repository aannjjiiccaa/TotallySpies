from functools import lru_cache
from sentence_transformers import SentenceTransformer
from abc import ABC, abstractmethod
from typing import List
from ..core.config import get_settings


class Embedder(ABC):
    @abstractmethod
    def embed(self, texts: List[str]) -> List[List[float]]:
        pass


class LocalEmbedder(Embedder):
    def __init__(self, model_name: str):
        self.model = SentenceTransformer(model_name)

    def embed(self, texts):
        return self.model.encode(texts, normalize_embeddings=True).tolist()


class APIEmbedder(Embedder):
    def __init__(self, client, model: str):
        self.client = client
        self.model = model

    def embed(self, texts):
        response = self.client.embeddings.create(
            model=self.model,
            input=texts
        )
        return [item.embedding for item in response.data]


@lru_cache(maxsize=1)
def get_embedder():
    settings = get_settings()
    return LocalEmbedder(settings.EMBEDDER_MODEL_NAME)