import json
from chromadb import PersistentClient
from src.core.config import get_settings
from urllib.parse import urlparse

def second_pass():
    settings = get_settings()
    client = PersistentClient(path=settings.PERSIST_DIR)
    collection = client.get_or_create_collection(
        name=settings.COLLECTION_NAME
    )

    results = collection.get(include=["ids", "documents", "metadatas"])

    for doc_id, document, metadata in zip(
        results["ids"],
        results["documents"],
        results["metadatas"]
    ):
        http_calls = json.loads(metadata.get("http_calls", "[]"))
        repo_http = json.loads(metadata.get("repo_http", "[]"))

        if not http_calls:
            continue
        new_nodes = find(http_calls) 

        if not new_nodes:
            continue

        repo_http.extend(new_nodes)

        repo_http = list({
            json.dumps(x, sort_keys=True)
            for x in repo_http
        })
        repo_http = [json.loads(x) for x in repo_http]

        metadata["repo_http"] = json.dumps(repo_http)
        collection.upsert(
            ids=[doc_id],
            documents=[document],
            metadatas=[metadata]
        )

def find(http_calls):
    settings = get_settings()
    client = PersistentClient(path=settings.PERSIST_DIR)

    collection = client.get_or_create_collection(
        name=settings.COLLECTION_NAME
    )
    new_nodes = []
    for call in http_calls:
        method = call.get("method")
        url = call.get("url")

        if not url:
            continue

        results = collection.get(include=["metadatas"])

        for metadata in results["metadatas"]:
            routes_raw = metadata.get("routes", "[]")

            try:
                routes = json.loads(routes_raw)
            except Exception:
                continue

            for route in routes:
                path = route.get("path")
                decorator = route.get("decorator")

                if not path:
                    continue

                if decorator==method and match(url, path):
                    new_nodes.append({
                        "target_file": route.get("file"),
                        "url": url
                    })

    return new_nodes

def match(url: str, route_path: str) -> bool:
    if not url or not route_path:
        return False
    parsed = urlparse(url)
    url_path = parsed.path
    url_path = url_path.rstrip("/")
    route_path = route_path.rstrip("/")

    if route_path == "" or route_path == "/":
        return url_path == "" or url_path == "/"

    if url_path == route_path:
        return True

    return False
