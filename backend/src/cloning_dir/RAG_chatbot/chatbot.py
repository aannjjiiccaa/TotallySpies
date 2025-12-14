from rag.retriever import answer_with_rag
from chromadb import PersistentClient
from core.config import get_settings


def answer(q):
    settings = get_settings()
    client = PersistentClient(path=settings.PERSIST_DIR)
    collection = client.get_or_create_collection(
        name=settings.COLLECTION_NAME
    )
    return answer_with_rag(collection, q)


if __name__ == '__main__':
    question = "Which file does any kind of calculation?"
    answer = answer(question)
    print(answer)
