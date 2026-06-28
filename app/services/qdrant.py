from langchain_qdrant import QdrantVectorStore

from app.core.config import settings
from app.services.embeddings import get_embeddings


def get_vector_store() -> QdrantVectorStore:
    return QdrantVectorStore.from_existing_collection(
        collection_name=settings.QDRANT_COLLECTION,
        embedding=get_embeddings(),
        url=settings.QDRANT_URL,
        api_key=settings.QDRANT_API_KEY or None,
    )


def create_vector_store_from_documents(documents) -> QdrantVectorStore:
    return QdrantVectorStore.from_documents(
        documents,
        embedding=get_embeddings(),
        collection_name=settings.QDRANT_COLLECTION,
        url=settings.QDRANT_URL,
        api_key=settings.QDRANT_API_KEY or None,
        force_recreate=False,
    )