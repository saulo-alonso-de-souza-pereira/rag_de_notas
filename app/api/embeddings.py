from fastapi import APIRouter

from app.services.embeddings import get_embeddings


router = APIRouter(
    prefix="/embeddings",
    tags=["embeddings"],
)


@router.get("/health")
async def embeddings_health():
    embeddings = get_embeddings()

    vetor = await embeddings.aembed_query("teste de embeddings locais")

    return {
        "status": "ok",
        "modelo": "local",
        "dimensoes": len(vetor),
    }