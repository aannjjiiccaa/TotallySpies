from pathlib import Path
from typing import List
from chromadb.api.models.Collection import Collection
from .llm import get_llm
import json


def build_http_interactions(collection, repo_path: str) -> List[str]:
    """
    Returns compact descriptions of HTTP interactions originating from this repo.
    """
    res = collection.get(
        where={"type": "file"},
        include=["metadatas"],
    )

    interactions = []

    for meta in res.get("metadatas", []):
        path = meta.get("path", "")
        if not path.startswith(repo_path + "/"):
            continue

        repo_http_raw = meta.get("repo_http")
        if not repo_http_raw:
            continue

        try:
            repo_http = json.loads(repo_http_raw)
        except Exception:
            continue

        source_file = Path(path).name

        for edge in repo_http:
            target = edge.get("target_file")
            url = edge.get("url")

            if not target or not url:
                continue

            target_repo = Path(target).parents[2].name  # repo folder name
            target_file = Path(target).name

            interactions.append(
                f"- {source_file} calls {target_repo}/{target_file} via {url}"
            )

    return interactions


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
                ]
            },
            include=["metadatas"],
        )

        entrypoints = [
                          f"- {Path(m['path']).name}: {m.get('short', '')}"
                          for m in ep_res.get("metadatas", [])
                          if m.get("path", "").startswith(repo_path + "/")
                      ][:max_entrypoints_per_repo]

        # ---------- HTTP interactions ----------
        http_interactions = build_http_interactions(collection, repo_path)

        http_block = (
            "\n".join(http_interactions[:5])
            if http_interactions
            else "- (No detected HTTP interactions)"
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

        HTTP Interactions:
        {http_block}
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
        Write a clear but very detailed, well-structured system-level summary that includes:
        
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
