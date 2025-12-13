from chromadb import PersistentClient
from src.core.config import get_settings
from src.rag.embedder import get_embedder
from src.rag.llm import get_llm
from src.utils.iterate_cloning_dir import iter_files, iter_chroma_entries, iter_dirs_bottom_up
from src.utils.process_file import get_description, get_embedding, get_connections,  add_to_base, process_directory, flush_file_buffer
import os


def main():
    settings = get_settings()
    llm = get_llm()
    embedder = get_embedder()
    client = PersistentClient(path=settings.PERSIST_DIR)
    collection = client.get_or_create_collection(
        name=settings.COLLECTION_NAME
    )

    buffer = []

    # ---------- PASS 1: FILES ----------
    for file in iter_files(settings.CLONING_DIR):
        description = get_description(file)
        connections = get_connections(file)
        if connections['language'] == 'unknown':
            continue

        buffer.append({
            "file": file,
            "description": description,
            "connections": connections,
        })

        if len(buffer) >= settings.BATCH_SIZE:
            flush_file_buffer(collection, buffer, embedder)
            buffer.clear()

    # flush remaining files
    if buffer:
        flush_file_buffer(collection, buffer, embedder)

    # ---------- PASS 2: DIRECTORIES ----------
    for dir_path in iter_dirs_bottom_up(settings.CLONING_DIR):
        process_directory(collection, dir_path)






if __name__ == '__main__':
    main()