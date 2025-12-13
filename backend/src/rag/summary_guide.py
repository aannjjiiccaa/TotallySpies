from pathlib import Path
from typing import List
from chromadb.api.models.Collection import Collection


def build_system_context(
    collection: Collection,
    max_dirs_per_repo: int = 5,
    max_entrypoints_per_repo: int = 3,
) -> str:
    """
    Build a structured, bounded system context from ChromaDB
    suitable for LLM summarization.
    """

    # ---------- Load repos ----------
    repo_res = collection.get(
        where={"type": "repo"},
        include=["metadatas"],
    )

    repos = repo_res.get("metadatas", [])
    if not repos:
        return "No repositories found."

    system_blocks: List[str] = []

    for repo_meta in repos:
        repo_path = repo_meta["path"]
        repo_name = Path(repo_path).name
        repo_short = repo_meta.get("short", "Repository component.")

        # ---------- Entrypoints ----------
        ep_res = collection.get(
            where={
                "$and": [
                    {"type": "file"},
                    {"role": "entrypoint"},
                    {"path": {"$contains": repo_path}},
                ]
            },
            include=["metadatas"],
        )

        entrypoints = []
        for m in ep_res.get("metadatas", [])[:max_entrypoints_per_repo]:
            entrypoints.append(
                f"- {Path(m['path']).name}: {m.get('short', '')}"
            )

        ep_block = (
            "\n".join(entrypoints)
            if entrypoints
            else "- (No explicit entrypoints detected)"
        )

        # ---------- Top-level directories ----------
        dir_res = collection.get(
            where={
                "$and": [
                    {"type": "dir"},
                    {"parent": repo_path},
                ]
            },
            include=["metadatas"],
        )

        dirs = []
        for m in dir_res.get("metadatas", [])[:max_dirs_per_repo]:
            dirs.append(
                f"- {Path(m['path']).name}: {m.get('short', '')}"
            )

        dir_block = (
            "\n".join(dirs)
            if dirs
            else "- (No top-level directories)"
        )

        # ---------- Build repo block ----------
        repo_block = f"""
REPOSITORY: {repo_name}

Purpose:
{repo_short}

Entrypoints:
{ep_block}

Architecture:
{dir_block}
""".strip()

        system_blocks.append(repo_block)

    return "\n\n".join(system_blocks)
