from pathlib import Path
import os


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