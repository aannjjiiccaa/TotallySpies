from pathlib import Path
from typing import List
from chromadb.api.models.Collection import Collection
from .llm import get_llm

def build_system_context(
    collection: Collection,
    max_dirs_per_repo: int = 5,
    max_entrypoints_per_repo: int = 3,
) -> str:

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



def generate_system_summary(system_context: str) -> str:
    """
    Generate a high-level system summary from structured repository context.
    """
    llm = get_llm()

    prompt = f"""
        You are a senior software architect writing documentation for a multi-repository system.
        
        Below is structured information extracted from the codebase.
        It includes repository purposes, entrypoints, and top-level architecture.
        
        SYSTEM CONTEXT:
        {system_context}
        
        TASK:
        Write a clear, well-structured system-level summary that includes:
        
        1) Overall system purpose
        2) Role of each repository
        3) How execution flows through the system (starting from entrypoints)
        4) How repositories interact with each other
        5) Where a new developer should start exploring the codebase
        
        RULES:
        - Base your explanation STRICTLY on the provided context.
        - Do NOT invent functionality, APIs, or integrations.
        - If something is unclear, state assumptions explicitly.
        - Prefer clarity and structure over verbosity.
        - Do NOT repeat the input verbatim.
        
        Write in professional technical documentation style.
        """

    return llm.generate(prompt)
