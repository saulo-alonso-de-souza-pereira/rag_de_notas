from fastapi import APIRouter, Depends

from app.api.deps import get_usuario_atual
from app.models.usuario import Usuario
from app.rag.chain import responder_pergunta_com_rag
from app.schemas.chat import RagPerguntaRequest, RagPerguntaResponse


router = APIRouter(
    prefix="/rag",
    tags=["rag"],
)


@router.post("/perguntar", response_model=RagPerguntaResponse)
async def perguntar(
    dados: RagPerguntaRequest,
    usuario_atual: Usuario = Depends(get_usuario_atual),
):
    return await responder_pergunta_com_rag(
        pergunta=dados.pergunta,
        usuario_id=usuario_atual.id,
    )