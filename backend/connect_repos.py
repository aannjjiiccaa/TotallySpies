from src.utils.iterate_cloning_dir import iter_chroma_nodes, update_chroma_node
from chromadb import PersistentClient
from src.core.config import get_settings
from src.rag.embedder import get_embedder
from src.rag.llm import get_llm
from src.utils.iterate_cloning_dir import iter_files, iter_chroma_entries, iter_dirs_bottom_up
from src.utils.process_file import get_description, get_embedding, get_connections,  add_to_base, process_directory, flush_file_buffer
import os


def second_pass():
    settings = get_settings()
    client = PersistentClient(path=settings.PERSIST_DIR)
    collection = client.get_or_create_collection(
        name=settings.COLLECTION_NAME
    )

    for node in iter_chroma_nodes(collection):
        new_node = find(node)
        if new_node is not None:
            update_chroma_node(new_node)





def find(node):
    """Return None if node doesnt need to be changed."""
    return None
