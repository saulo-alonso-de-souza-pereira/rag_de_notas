from dataclasses import dataclass

from langchain_core.documents import Document
from qdrant_client.models import FieldCondition, Filter, MatchValue

from app.core.config import settings
from app.rag.vector_store import get_vector_store


@dataclass
class DocumentoRecuperado:
    documento: Document
    score: float


async def buscar_documentos_relevantes(
    pergunta: str,
    usuario_id: int,
    k: int | None = None,
    score_threshold: float | None = None,
) -> list[DocumentoRecuperado]:
    vector_store = get_vector_store()

    limite = k or settings.RAG_TOP_K
    score_minimo = (
        score_threshold
        if score_threshold is not None
        else settings.RAG_SCORE_THRESHOLD
    )

    filtro_usuario = Filter(
        must=[
            FieldCondition(
                key="metadata.usuario_id",
                match=MatchValue(value=usuario_id),
            )
        ]
    )

    resultados = await vector_store.asimilarity_search_with_score(
        query=pergunta,
        k=limite,
        filter=filtro_usuario,
        score_threshold=score_minimo,
    )

    return [
        DocumentoRecuperado(
            documento=documento,
            score=float(score),
        )
        for documento, score in resultados
    ]