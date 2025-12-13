from pathlib import Path
from .llm import get_llm


def is_under_repo(path: str, repo_root: str) -> bool:
    repo_root = repo_root.rstrip("/") + "/"
    return path.startswith(repo_root)


def compress_directory_descriptions(dirs, max_items=15):
    """
    Compress many directory descriptions into a short architectural overview.
    """
    llm = get_llm()

    dirs = dirs[:max_items]

    text = "\n".join(f"- {path}: {desc}" for path, desc in dirs)

    prompt = f"""
    Summarize the following directory purposes into a concise architectural overview.
    Preserve key components and responsibilities.
    
    {text}
    """

    return llm.generate(prompt)


def build_repo_context(
    collection,
    repo_root: str,
    max_dirs: int = 50,
    max_entrypoints: int = 20,
):
    repo_root = str(Path(repo_root).resolve())

    # ------------------
    # Repo short description
    # ------------------
    repo_res = collection.get(ids=[repo_root], include=["metadatas"])
    repo_meta = (repo_res.get("metadatas") or [{}])[0]
    repo_desc = repo_meta.get(
        "short",
        "Repository composed of multiple cooperating subsystems."
    )

    # ------------------
    # Directories (scoped, SHORT ONLY)
    # ------------------
    dirs_res = collection.get(
        where={"type": "dir"},
        include=["metadatas"],
    )

    dirs = sorted(
        [
            (m["path"], m["short"])
            for m in (dirs_res.get("metadatas") or [])
            if m
            and m.get("path")
            and m.get("short")
            and is_under_repo(m["path"], repo_root)
        ],
        key=lambda x: (x[0].count("/"), x[0]),
    )[:max_dirs]

    dir_overview = compress_directory_descriptions(dirs)

    # ------------------
    # Entry points (scoped, SHORT ONLY)
    # ------------------
    ep_res = collection.get(
        where={"type": "file", "role": "entrypoint"},
        include=["metadatas"],
    )

    entrypoints = sorted(
        [
            (m["path"], m["short"])
            for m in (ep_res.get("metadatas") or [])
            if m
            and m.get("path")
            and m.get("short")
            and is_under_repo(m["path"], repo_root)
        ],
        key=lambda x: x[0],
    )[:max_entrypoints]

    return repo_desc, dir_overview, entrypoints


def generate_full_repo_summary(collection, repo_root: str) -> str:
    llm = get_llm()

    repo_desc, dir_overview, entrypoints = build_repo_context(
        collection, repo_root
    )

    ep_section = "\n".join(
        f"- {path}: {desc}" for path, desc in entrypoints
    )

    prompt = f"""
    You are writing high-quality developer documentation for a codebase.
    
    Repository overview:
    {repo_desc}
    
    Architecture overview (derived from directories):
    {dir_overview}
    
    Entry points:
    {ep_section}
    
    Write a detailed README-style summary with the following sections:
    
    1) What this repository does
    2) Architecture overview
    3) Key entry points and execution flow
    4) How to run / use (best effort, clearly label assumptions)
    5) Where to make changes
    6) Glossary of important concepts
    
    Constraints:
    - Do not invent commands or technologies.
    - Base reasoning strictly on provided information.
    - Prefer clarity and structure.
    """

    return llm.generate(prompt)


def generate_repo_capsule(collection, repo_root: str) -> str:
    llm = get_llm()

    repo_desc, dir_overview, entrypoints = build_repo_context(
        collection, repo_root
    )

    ep_list = "\n".join(path for path, _ in entrypoints)

    prompt = f"""
    Summarize the following repository into a short architectural capsule.
    
    Repository description:
    {repo_desc}
    
    Architecture overview:
    {dir_overview}
    
    Entry points:
    {ep_list}
    
    Return:
    - Purpose
    - Main responsibilities
    - How it is likely used by other repositories
    (Keep it concise.)
    """

    return llm.generate(prompt)


def build_multi_repo_context(collection, repo_roots: list[str]):
    contexts = []

    for repo_root in repo_roots:
        summary = generate_full_repo_summary(collection, repo_root)
        contexts.append(
                f"""
    REPOSITORY: {repo_root}
    
    {summary}
    """
            )

    return "\n\n".join(contexts)


def generate_multi_repo_overview(collection, repo_roots: list[str]) -> str:
    llm = get_llm()

    capsules = []

    for repo_root in repo_roots:
        capsule = generate_repo_capsule(collection, repo_root)
        capsules.append(
            f"""
REPOSITORY: {repo_root}

{capsule}
"""
        )

    repo_context = "\n\n".join(capsules)

    prompt = f"""
    You are analyzing a system composed of multiple software repositories.
    
    Below are architectural capsules for each repository.
    
    {repo_context}
    
    Explain how these repositories work together.
    
    Include:
    1) System-level overview
    2) Role of each repository
    3) Interactions and dependencies
    4) Entry points and execution flow
    5) Developer workflow across repos
    6) Assumptions and inferred relationships (clearly labeled)
    
    Constraints:
    - Do not invent integrations.
    - Reason strictly from provided information.
    - Prefer clarity over certainty.
    """

    return llm.generate(prompt)




