from chromadb import PersistentClient
from ..src.core.config import get_settings


def print_all_entries_with_embeddings():
    settings = get_settings()

    client = PersistentClient(path=settings.PERSIST_DIR)
    collection = client.get_collection(name=settings.COLLECTION_NAME)

    results = collection.get(
        include=["documents", "metadatas", "embeddings"]
    )

    ids = results.get("ids", [])
    documents = results.get("documents", [])
    metadatas = results.get("metadatas", [])
    embeddings = results.get("embeddings", [])

    for i, (doc_id, doc, meta, emb) in enumerate(
        zip(ids, documents, metadatas, embeddings),
        start=1,
    ):
        print("=" * 80)
        print(f"ENTRY #{i}")
        print(f"ID: {doc_id}")

        print("\nMETADATA:")
        for k, v in meta.items():
            print(f"  {k}: {v}")

        print("\nDOCUMENT (detailed description):")
        print(doc)

        if emb is not None:
            print("\nEMBEDDING:")
            print(emb)
            print(f"\nEMBEDDING DIMENSION: {len(emb)}")
        else:
            print("\nEMBEDDING: None")


if __name__ == "__main__":
    print_all_entries_with_embeddings()
