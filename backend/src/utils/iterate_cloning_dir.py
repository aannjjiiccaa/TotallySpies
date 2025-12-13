from pathlib import Path
import os
from typing import Iterator, Dict, Any
from chromadb.api.models.Collection import Collection


def iter_chroma_nodes(
    collection: Collection,
    include_embeddings: bool = False,
) -> Iterator[Dict[str, Any]]:
    include = ["documents", "metadatas"]
    if include_embeddings:
        include.append("embeddings")

    results = collection.get(include=include)

    ids = results.get("ids", [])
    documents = results.get("documents", [])
    metadatas = results.get("metadatas", [])
    embeddings = results.get("embeddings", [])

    for i in range(len(ids)):
        yield {
            "id": ids[i],
            "document": documents[i],
            "metadata": metadatas[i],
            "embedding": embeddings[i] if include_embeddings else None,
        }


def update_chroma_node(
    collection,
    node: dict,
):
    collection.upsert(
        ids=[node["id"]],
        documents=[node["document"]],
        metadatas=[node["metadata"]],
        embeddings=[node["embedding"]] if node["embedding"] is not None else None,
    )


def iter_files(cloning_dir: str | Path):
    cloning_dir = Path(cloning_dir)

    for repo in cloning_dir.iterdir():
        if not repo.is_dir():
            continue

        for root, dirs, files in os.walk(repo):
            for file in files:
                file_path = Path(root) / file
                yield file_path


def iter_chroma_entries(collection, batch_size=100):
    offset = 0

    while True:
        batch = collection.get(
            include=["documents", "metadatas", "ids"],
            limit=batch_size,
            offset=offset,
        )

        if not batch["ids"]:
            break

        for i in range(len(batch["ids"])):
            yield {
                "id": batch["ids"][i],
                "document": batch["documents"][i],
                "metadata": batch["metadatas"][i],
            }

        offset += batch_size


def iter_dirs_bottom_up(root: str):
    """
    Yield all directories bottom-up (deepest first).
    """
    root = Path(root).resolve()

    for dirpath, _, _ in os.walk(root, topdown=False):
        yield Path(dirpath)