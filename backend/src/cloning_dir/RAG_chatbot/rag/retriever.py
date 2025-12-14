from typing import List, Dict
from .embedder import get_embedder
import json
from pathlib import Path
from typing import List, Dict


ENTRYPOINT_KEYWORDS = {
    "run", "start", "entry", "main", "initialize", "boot",
    "launch", "execute", "cli", "server", "app", "entrypoints", "entrypoint", "http", "https", "api"
}


def is_entrypoint_query(query: str) -> bool:
    q = query.lower()
    return any(k in q for k in ENTRYPOINT_KEYWORDS)


def build_rag_context(
    retrieved: List[Dict],
    prefer_entrypoints: bool,
    max_files: int = 4,
    max_dirs: int = 2,
) -> str:

    entrypoints = []
    files = []
    dirs = []
    repos = []

    for item in retrieved:
        meta = item["metadata"]
        node_type = meta.get("type")

        if node_type == "file" and meta.get("role") == "entrypoint":
            entrypoints.append(item)
        elif node_type == "file":
            files.append(item)
        elif node_type == "dir":
            dirs.append(item)
        elif node_type == "repo":
            repos.append(item)

    blocks = []

    # ---------- Repos ----------
    for r in repos[:1]:
        blocks.append(
            f"""
REPOSITORY:
{Path(r['path'])}

Purpose:
{r['metadata'].get('short', '')}
""".strip()
        )

    # ---------- Entrypoints ----------
    if prefer_entrypoints:
        if entrypoints:
            blocks.append(
                "ENTRYPOINTS:\n" + "\n".join(
                    f"- {Path(ep['path'])}: {ep['metadata'].get('short', '')}"
                    for ep in entrypoints[:3]
                )
            )
        else:
            blocks.append(
                "ENTRYPOINTS:\n- (No explicit entrypoints detected in retrieved context)"
            )

    # ---------- Files ----------
    for f in files[:max_files]:
        meta = f["metadata"]

        http_calls = []
        try:
            http_calls = json.loads(meta.get("http_calls", "[]"))
        except Exception:
            pass

        http_block = ""
        if http_calls:
            http_block = "\nHTTP Calls:\n" + "\n".join(
                f"- {c.get('method', '').upper()} {c.get('url', '')}"
                for c in http_calls[:2]
            )

        blocks.append(
            f"""
FILE: {Path(f['path'])}
Purpose: {meta.get('short', '')}

Details:
{f['document'][:800]}
{http_block}
""".strip()
        )

    # ---------- Directories ----------
    for d in dirs[:max_dirs]:
        blocks.append(
            f"""
DIRECTORY: {Path(d['path'])}
Purpose: {d['metadata'].get('short', '')}
""".strip()
        )

    return "\n\n".join(blocks)


class ChromaRetriever:
    def __init__(self, collection, top_k: int = 8):
        self.collection = collection
        self.top_k = top_k
        self.embedder = get_embedder('search_query')

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


from .llm import get_llm


def answer_with_rag(
    collection,
    question: str,
    top_k: int = 8,
) -> str:
    retriever = ChromaRetriever(collection, top_k=top_k)
    llm = get_llm()

    retrieved = retriever.retrieve(question)
    print("RETRIEVED NODES:")
    for r in retrieved:
        print(r["metadata"].get("type"), r["metadata"].get("role"), r["path"])

    if not retrieved:
        return "I could not find relevant information in the codebase."

    prefer_entrypoints = is_entrypoint_query(question)

    context = build_rag_context(
        retrieved,
        prefer_entrypoints=prefer_entrypoints,
    )

    prompt = f"""
You are a senior software engineer helping a developer understand a codebase.

The following context was retrieved from the repository.
It includes file purposes, architecture summaries, and known interactions.

CONTEXT:
{context}

QUESTION:
{question}

INSTRUCTIONS:
- Answer strictly based on the provided context.
- If information is missing, say so explicitly.
- When relevant, explain execution flow and entrypoints.
- Be concise but precise.
- Do NOT invent APIs, functions, or behavior.

ANSWER:
"""
    print(prompt)

    return llm.generate(prompt)

