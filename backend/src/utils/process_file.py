from src.utils.parsers import detect_language, parse_python
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


def get_connections(file):
    lang = detect_language(file)

    if lang == "python":
        return parse_python(file)

    return {
        "language": "unknown",
        "imports": [],
        "symbols_defined": [],
        "symbols_used": []
    }


def get_embedding(description):
    embedder = get_embedder()
    return embedder.embed(description)


def get_description(file_path: str) -> str:
    llm = get_llm()

    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    code = path.read_text(encoding="utf-8")

    prompt = f"""
        You are a senior software engineer.
        
        Describe what the following code does so it can be understood for all levels of engineers.
        Be concise and high-level.
        Do NOT repeat the code.
        Do NOT include markdown.
        Do NOT include explanations unrelated to the code.
        
        CODE:
        {code}
        """

    return llm.generate(prompt)


def add_to_base(collection, description, embedding, connections, path):
    settings = get_settings()

    path = Path(path).resolve()
    repo_root = Path(settings.CLONING_DIR).resolve()

    # --- Determine node type ---
    if path == repo_root:
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
        "parent": parent,
    }

    # --- File-specific metadata ---
    if node_type == "file" and connections is not None:
        filename = path.name

        # Determine role
        role = "entrypoint" if filename in ENTRYPOINT_FILENAMES else "module"

        metadata.update({
            "role": role,
            "language": connections.get("language"),
            "imports": json.dumps(connections.get("imports", [])),
            "symbols_defined": json.dumps(connections.get("symbols_defined", [])),
            "symbols_used": json.dumps(connections.get("symbols_used", [])),
        })

    collection.add(
        ids=[str(path)],
        documents=[description],
        embeddings=[embedding],
        metadatas=[metadata],
    )


def process_directory(collection, dir_path: str):
    dir_path = str(Path(dir_path).resolve())

    # Get immediate children: files + dirs
    results = collection.get(
        where={
            "$or": [
                {"type": "file", "parent": dir_path},
                {"type": "dir", "parent": dir_path},
            ]
        }
    )

    descriptions = results.get("documents", [])

    if not descriptions:
        # empty directory → skip
        return

    llm = get_llm()
    embedder = get_embedder()

    prompt = f"""
        Describe the purpose of this directory based on its contents.
        Be concise and high-level.
        
        CONTENTS:
        {chr(10).join(descriptions)}
        """

    description = llm.generate(prompt)
    embedding = embedder.embed([description])[0]

    # connections = None (dirs do not have connections)
    add_to_base(
        collection=collection,
        description=description,
        embedding=embedding,
        connections=None,
        path=dir_path,
    )