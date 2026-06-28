from fastapi import APIRouter

from app.services.qdrant import get_vector_store


router = APIRouter(
    prefix="/qdrant",
    tags=["qdrant"],
)


@router.get("/health")
def qdrant_health():
    get_vector_store()

    return {
        "status": "ok",
        "vector_store": "qdrant",
    }