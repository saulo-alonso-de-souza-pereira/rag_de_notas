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
    resultados = await buscar_documentos_relevantes(
        pergunta=pergunta,
        usuario_id=usuario_atual.id,
    )

    return {
        "total": len(resultados),
        "documentos": [
            {
                "conteudo": resultado.documento.page_content,
                "metadata": resultado.documento.metadata,
                "score": round(resultado.score, 4),
            }
            for resultado in resultados
        ],
    }