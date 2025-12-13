from chromadb import PersistentClient
from sentence_transformers import SentenceTransformer
from src.core.config import get_settings
from src.rag.embedder import get_embedder
from src.rag.llm import get_llm
import os


settings = get_settings()
llm = get_llm()
embedder = get_embedder()


def main():
    pass

if __name__ == '__main__':
    main()









