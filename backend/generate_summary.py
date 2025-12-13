from src.rag.summary_guide import generate_system_summary, build_system_context
from chromadb import PersistentClient
from src.core.config import get_settings


def main():
    settings = get_settings()
    client = PersistentClient(path=settings.PERSIST_DIR)
    collection = client.get_or_create_collection(
        name=settings.COLLECTION_NAME
    )
    context = build_system_context(collection)
    return generate_system_summary(context)


if __name__ == '__main__':
    main()