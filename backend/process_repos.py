import datetime
import json
from chromadb import PersistentClient
from src.utils.graph_builder import build_graph
from src.utils.services_registry import build_service_registry
from src.core.config import get_settings
from src.rag.embedder import get_embedder
from src.rag.llm import get_llm
from src.utils.iterate_cloning_dir import iter_files, iter_chroma_entries, iter_dirs_bottom_up
from src.utils.process_file import get_description, get_embedding, get_connections,  add_to_base, process_directory
import os


settings = get_settings()
llm = get_llm()
embedder = get_embedder()

def get_repo_name(file_path):
    return os.path.relpath(file_path, settings.CLONING_DIR).split(os.sep)[0]

def main():
    results = []
    for file in iter_files(settings.CLONING_DIR):
        repo_name = get_repo_name(file)
        connections = get_connections(file)

        results.append({
            "repo": repo_name,
            "file": str(file),
            **connections
        })

    services = build_service_registry(results)
    graph = build_graph(results, services)

    output = {
        "project": {
            "repos": list(services.keys())
        },
        **graph,
        "metadata": {
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "tool": "Atlas",
            "version": "0.1"
        }
    }

    with open("graph.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    client = PersistentClient(path=settings.PERSIST_DIR)
    collection = client.get_or_create_collection(name=settings.COLLECTION_NAME)
    for file_data in results:
        description = get_description(file_data["file"])
        embeddings = get_embedding(description)
        add_to_base(collection, description, embeddings, file_data["connections"], file_data["file"])

    for dir_path in iter_dirs_bottom_up(settings.CLONING_DIR):
        process_directory(collection, dir_path)


if __name__ == '__main__':
    main()









