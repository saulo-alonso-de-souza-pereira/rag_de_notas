from fastapi import APIRouter, Depends

from app.api.deps import get_usuario_atual
from app.models.usuario import Usuario
from app.rag.retriever import buscar_documentos_relevantes


router = APIRouter(
    prefix="/retriever",
    tags=["retriever"],
)


@router.get("/buscar")
async def buscar(
    pergunta: str,
    usuario_atual: Usuario = Depends(get_usuario_atual),
):
    documentos = await buscar_documentos_relevantes(
        pergunta=pergunta,
        usuario_id=usuario_atual.id,
    )

    return {
        "total": len(documentos),
        "documentos": [
            {
                "conteudo": doc.page_content,
                "metadata": doc.metadata,
            }
            for doc in documentos
        ],
    }