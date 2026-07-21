from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_usuario_atual
from app.models.usuario import Usuario
from app.rag.chain import responder_pergunta_com_rag
from app.rag.general_chat import responder_conversa_geral
from app.rag.note_creator import tentar_criar_nota_por_linguagem_natural
from app.rag.router import classificar_intencao
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
    intencao = await classificar_intencao(dados.pergunta)

    if intencao == "criar_nota":
        resultado = await tentar_criar_nota_por_linguagem_natural(
            db=db,
            usuario_id=usuario_atual.id,
            mensagem=dados.pergunta,
        )

        if resultado:
            return resultado

        return {
            "resposta": "Não consegui identificar título e conteúdo para criar a nota.",
            "fontes": [],
        }

    if intencao == "consultar_notas":
        return await responder_pergunta_com_rag(
            pergunta=dados.pergunta,
            usuario_id=usuario_atual.id,
        )

    return await responder_conversa_geral(
        mensagem=dados.pergunta,
    )
