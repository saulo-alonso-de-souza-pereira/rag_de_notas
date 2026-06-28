from langchain_qdrant import QdrantVectorStore

from app.core.config import settings
from app.services.embeddings import get_embeddings


def get_vector_store() -> QdrantVectorStore:
    return QdrantVectorStore.from_existing_collection(
        embedding=get_embeddings(),
        collection_name=settings.QDRANT_COLLECTION,
        url=settings.QDRANT_URL,
        api_key=settings.QDRANT_API_KEY or None,
    )