from chromadb import PersistentClient
from src.core.config import get_settings
from src.rag.embedder import get_embedder
from src.rag.llm import get_llm
from src.utils.iterate_cloning_dir import iter_files, iter_chroma_entries, iter_dirs_bottom_up
from src.utils.process_file import get_description, get_embedding, get_connections,  add_to_base, process_directory
import os


settings = get_settings()
llm = get_llm()
embedder = get_embedder()




def main():
    client = PersistentClient(path=settings.PERSIST_DIR)
    collection = client.get_or_create_collection(name=settings.COLLECTION_NAME)
    for file in iter_files(settings.CLONING_DIR):
        description = get_description(file)
        embeddings = get_embedding(description)
        connections = get_connections(file)
        add_to_base(collection, description, embeddings, connections, file)

    for dir_path in iter_dirs_bottom_up(settings.CLONING_DIR):
        process_directory(collection, dir_path)






if __name__ == '__main__':
    main()









