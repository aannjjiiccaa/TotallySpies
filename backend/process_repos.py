from chromadb import PersistentClient
from sentence_transformers import SentenceTransformer
from src.core.config import get_settings
from src.rag.embedder import get_embedder
from src.rag.llm import get_llm
from src.utils.iterate_cloning_dir import iter_files
from src.utils.process_file import get_description, get_embedding, get_connections
import os


settings = get_settings()
llm = get_llm()
embedder = get_embedder()


def main():
    for file in iter_files(settings.CLONING_DIR):
        description = get_description()
        embeddings = get_embedding()
        connections = get_connections()



if __name__ == '__main__':
    main()









