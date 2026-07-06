from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_usuario_atual
from app.models.usuario import Usuario
from app.rag.chain import responder_pergunta_com_rag
from app.rag.note_creator import tentar_criar_nota_por_linguagem_natural
from app.schemas.chat import RagPerguntaRequest, RagPerguntaResponse


router = APIRouter(
    prefix="/rag",
    tags=["rag"],
)


@router.post("/perguntar", response_model=RagPerguntaResponse)
async def perguntar(
    dados: RagPerguntaRequest,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_usuario_atual),
):
    resultado_criacao = await tentar_criar_nota_por_linguagem_natural(
        db=db,
        usuario_id=usuario_atual.id,
        mensagem=dados.pergunta,
    )

    if resultado_criacao:
        return resultado_criacao

    return await responder_pergunta_com_rag(
        pergunta=dados.pergunta,
        usuario_id=usuario_atual.id,
    )