import json
from chromadb import PersistentClient
from ..core.config import get_settings
from pathlib import Path


def normalize_path(path: str, cloning_dir: str) -> str:
    p = Path(path)
    return str(p.relative_to(cloning_dir)).replace("\\", "/")


def extract_repo(path: str, cloning_dir: str) -> str:
    rel = Path(path).relative_to(cloning_dir)
    parts = rel.parts
    return parts[0] if len(parts) > 0 else ""

def extract_name(path: str) -> str:
    return path.split('/')[-1]


def build_graph():
    settings = get_settings()
    cloning_dir = Path(settings.CLONING_DIR)
    client = PersistentClient(path=settings.PERSIST_DIR)
    collection = client.get_or_create_collection(
        name=settings.COLLECTION_NAME
    )

    results = collection.get(include=["documents", "metadatas"])

    nodes = []
    edges = []
    node_map = {}

    for doc_id, document, metadata in zip(
        results["ids"],
        results["documents"],
        results["metadatas"]
    ):
        if metadata.get("type") != "file":
            continue

        file_path = metadata.get("path", doc_id)
        norm_path = normalize_path(file_path, str(cloning_dir))
        repo = extract_repo(file_path, str(cloning_dir))
        description = document
        name = extract_name(doc_id)

        node = {
            "id": doc_id,
            "name": name,
            "repo": repo,
            "description": description,
        }

        nodes.append(node)
        node_map[doc_id] = node

    for doc_id, document, metadata in zip(
        results["ids"],
        results["documents"],
        results["metadatas"]
    ):
        src_path = normalize_path(metadata.get("path", doc_id), str(cloning_dir))
        imports = metadata.get("imports", [])
        if isinstance(imports, str):
            imports = json.loads(imports)

        for imp in imports:
            try:
                target = imp
            except Exception:
                continue
            if target in node_map:
                edges.append({"from": doc_id, "to": target, "type": "import"})

        repo_http = metadata.get("repo_http", [])
        if isinstance(repo_http, str):
            repo_http = json.loads(repo_http)

        for call in repo_http:
            target_file = call.get("target_file")
            if not target_file:
                continue
            try:
                target = target_file
            except Exception:
                continue
            if target in node_map:
                edges.append({"from": doc_id, "to": target, "type": "http"})

    graph = {"nodes": nodes, "edges": edges}

    settings = get_settings()
    graph_path = Path(settings.JSON_PATH)
    if not graph_path.is_absolute():
        graph_path = Path.cwd() / graph_path
    graph_path.parent.mkdir(parents=True, exist_ok=True)

    with open(graph_path, "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2)

    print(f"Graph written: {len(nodes)} nodes, {len(edges)} edges -> {graph_path}")

