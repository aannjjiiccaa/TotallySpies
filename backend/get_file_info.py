from typing import Optional, Dict
from chromadb.api.models.Collection import Collection


def get_node_by_id(
    collection: Collection,
    node_id: str,
) -> Optional[Dict]:

    include = ["documents", "metadatas"]

    res = collection.get(
        ids=[node_id],
        include=include,
    )

    if not res.get("ids"):
        return None

    return {
        "id": res["ids"][0],
        "document": res["documents"][0] if "documents" in res else None,
        "metadata": res["metadatas"][0] if "metadatas" in res else None,
    }
