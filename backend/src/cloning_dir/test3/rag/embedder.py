from functools import lru_cache
from sentence_transformers import SentenceTransformer
from abc import ABC, abstractmethod
from typing import List
from ..core.config import get_settings
import cohere
from typing import List, Union


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
    def __init__(
        self,
        api_key: str,
        model: str = "embed-english-v3.0",
        input_type: str = "search_document",
    ):
        self.client = cohere.Client(api_key)
        self.model = model
        self.input_type = input_type

    def embed(self, texts: Union[str, List[str]]) -> List[List[float]]:
        """
        Embed one or many texts using Cohere.
        Always returns a list of embeddings.
        """
        if isinstance(texts, str):
            texts = [texts]

        response = self.client.embed(
            texts=texts,
            model=self.model,
            input_type=self.input_type,
        )

        return response.embeddings


@lru_cache(maxsize=1)
def get_embedder(input_type="search_document"):
    settings = get_settings()
    return APIEmbedder(
        settings.COHERE_API_KEY,
        settings.COHERE_EMBEDDER_MODEL,
        input_type=input_type,
    )