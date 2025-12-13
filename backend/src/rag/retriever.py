from typing import List, Dict
from .embedder import get_embedder


class ChromaRetriever:
    def __init__(self, collection, top_k: int = 8):
        self.collection = collection
        self.top_k = top_k
        self.embedder = get_embedder()

    def retrieve(self, query: str) -> List[Dict]:
        """
        Returns a list of retrieved nodes:
        [
          {
            "type": "file" | "dir" | "repo",
            "path": "...",
            "document": "...",
            "metadata": {...},
            "score": float
          }
        ]
        """

        query_embedding = self.embedder.embed([query])[0]

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=self.top_k,
            include=["documents", "metadatas", "distances"],
        )

        items = []
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            items.append({
                "type": meta.get("type"),
                "path": meta.get("path"),
                "document": doc,
                "metadata": meta,
                "score": float(dist),
            })

        return items
