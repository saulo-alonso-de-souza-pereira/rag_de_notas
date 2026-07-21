import json

from sqlalchemy.orm import Session

from app.models.nota import Nota
from app.rag.indexer import indexar_notas_usuario
from app.services.ollama import get_llm


CRIAR_NOTA_PROMPT = """
Extraia da mensagem do usuário os dados necessários para criar uma nota.

Responda APENAS com JSON válido, sem markdown ou explicações.

Quando houver uma solicitação para criar uma nota, use:

{{
  "deve_criar": true,
  "titulo": "título da nota",
  "conteudo": "conteúdo da nota"
}}

Quando não houver uma solicitação para criar uma nota, use:

{{
  "deve_criar": false,
  "titulo": null,
  "conteudo": null
}}

Mensagem do usuário:

{mensagem}
"""


async def tentar_criar_nota_por_linguagem_natural(
    db: Session,
    usuario_id: int,
    mensagem: str,
) -> dict | None:
    llm = get_llm()

    resposta = await llm.ainvoke(
        CRIAR_NOTA_PROMPT.format(mensagem=mensagem)
    )

    try:
        dados = json.loads(resposta.content)
    except json.JSONDecodeError:
        return None

    if not dados.get("deve_criar"):
        return None

    titulo = dados.get("titulo")
    conteudo = dados.get("conteudo")

    if not titulo or not conteudo:
        return {
            "resposta": "Para criar uma nota, informe título e conteúdo.",
            "fontes": [],
        }

    nota = Nota(
        titulo=titulo,
        conteudo=conteudo,
        usuario_id=usuario_id,
    )

    db.add(nota)
    db.commit()
    db.refresh(nota)

    indexar_notas_usuario(db=db, usuario_id=usuario_id)

    return {
        "resposta": f"Nota criada com sucesso: {nota.titulo}",
        "fontes": [
            {
                "nota_id": nota.id,
                "titulo": nota.titulo,
                "conteudo": nota.conteudo,
                "usuario_id": nota.usuario_id,
            }
        ],
    }