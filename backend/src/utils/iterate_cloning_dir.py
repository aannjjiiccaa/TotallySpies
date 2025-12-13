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
