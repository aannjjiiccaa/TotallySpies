from .parsers import detect_language, parse_python
from ..rag.embedder import get_embedder
from ..rag.llm import get_llm
from pathlib import Path
import json
from ..core.config import get_settings


ENTRYPOINT_FILENAMES = {
    "main.py",
    "app.py",
    "server.py",
    "index.py",
    "index.js",
    "index.ts",
    "cli.py",
}


def relpath(p, root):
    p = str(Path(p))
    root = str(Path(root))
    return p.replace(root.rstrip("/") + "/", "./")


def get_connections(file):
    lang = detect_language(file)

    if lang == "python":
        return parse_python(file)

    return {
        "language": "unknown",
        "imports": [],
        "packages": [],
        "symbols_defined": [],
        "symbols_used": [],
        "http_calls": []
    }


def get_embedding(description):
    embedder = get_embedder()
    return embedder.embed(description)


def get_description(file_path: str) -> dict:
    llm = get_llm()

    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    code = path.read_text(encoding="utf-8", errors="ignore")

    prompt = f"""
    You are a senior software engineer analyzing a source code file.
    
    Return STRICT JSON with the following fields:
    - "short": exactly ONE sentence describing the file’s purpose at a high level
    - "detailed": a clear, structured explanation of what the file does (max 150 words)
    
    Rules:
    - Do NOT repeat the code.
    - Do NOT include markdown.
    - Do NOT include information not inferable from the code.
    - The "short" field must be suitable for architecture-level summaries.
    
    CODE:
    {code}
    """

    response = llm.generate(prompt)

    try:
        return json.loads(response)
    except json.JSONDecodeError:
        # Fallback safety (important for hackathons)
        return {
            "short": response.strip().split(".")[0] + ".",
            "detailed": response.strip(),
        }


def add_to_base(
    collection,
    detailed_description: str,
    embedding: list[float],
    short_description: str,
    connections: dict | None,
    path: str | Path,
):
    settings = get_settings()

    path = Path(path).resolve()
    cloning_root = Path(settings.CLONING_DIR).resolve()

    # --- Determine node type ---
    if path.is_dir() and path.parent == cloning_root:
        node_type = "repo"
        parent = None
    elif path.is_dir():
        node_type = "dir"
        parent = str(path.parent)
    else:
        node_type = "file"
        parent = str(path.parent)

    metadata = {
        "type": node_type,
        "path": str(path),
        "short": short_description,
    }

    if parent is not None:
        metadata["parent"] = parent

    # --- File-specific metadata ---
    if node_type == "file" and connections is not None:
        filename = path.name
        role = "entrypoint" if filename in ENTRYPOINT_FILENAMES else "module"

        metadata.update({
            "role": role,
            "language": connections.get("language"),
            "imports": json.dumps(connections.get("imports", [])),
            "symbols_defined": json.dumps(connections.get("symbols_defined", [])),
            "symbols_used": json.dumps(connections.get("symbols_used", [])),
            "http_calls": json.dumps(connections.get("http_calls", [])),
            "routes": json.dumps(connections.get("routes", [])),
        })

    # --- Store in Chroma ---
    collection.add(
        ids=[str(path)],
        documents=[detailed_description],
        embeddings=[embedding],
        metadatas=[metadata],
    )


def flush_file_buffer(collection, buffer, embedder):
    # Embed ONLY detailed descriptions
    detailed_texts = [
        item["description"]["detailed"] for item in buffer
    ]

    detailed_embeddings = embedder.embed(detailed_texts)

    for item, embedding in zip(buffer, detailed_embeddings):
        add_to_base(
            collection=collection,
            detailed_description=item["description"]["detailed"],
            short_description=item["description"]["short"],
            embedding=embedding,
            connections=item["connections"],
            path=item["file"],
        )


def process_directory(collection, dir_path: str):
    dir_path = str(Path(dir_path).resolve())

    # Get immediate children (files + dirs)
    results = collection.get(
        where={
            "$or": [
                {
                    "$and": [
                        {"type": "file"},
                        {"parent": dir_path},
                    ]
                },
                {
                    "$and": [
                        {"type": "dir"},
                        {"parent": dir_path},
                    ]
                },
            ]
        },
        include=["metadatas"],
    )

    metadatas = results.get("metadatas", [])

    # Collect SHORT summaries from children
    short_children = [
        m["short"]
        for m in metadatas
        if m and m.get("short")
    ]

    if not short_children:
        # Empty directory → skip
        return

    llm = get_llm()
    embedder = get_embedder()

    # ---------- Generate directory summaries ----------
    prompt = f"""
    You are analyzing a source code directory.
    
    Based on the following brief descriptions of its contents, return STRICT JSON:
    
    - "short": one sentence describing the directory’s overall purpose
    - "detailed": a clear architectural explanation of the directory’s role (max 120 words)
    
    Rules:
    - Do NOT repeat the inputs verbatim.
    - Do NOT invent functionality.
    - Do NOT include markdown.
    
    CONTENTS:
    {chr(10).join(f"- {s}" for s in short_children)}
    """

    response = llm.generate(prompt)

    try:
        desc = json.loads(response)
    except Exception:
        # Safety fallback
        desc = {
            "short": short_children[0],
            "detailed": response.strip(),
        }

    # ---------- Embed ONLY detailed description ----------
    embedding = embedder.embed(desc["detailed"])[0]

    # ---------- Store directory via add_to_base ----------
    add_to_base(
        collection=collection,
        detailed_description=desc["detailed"],
        short_description=desc["short"],
        embedding=embedding,
        connections=None,
        path=dir_path,
    )