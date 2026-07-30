import json

from sqlalchemy.orm import Session
from app.rag.router import limpar_resposta_json

from app.models.nota import Nota
from app.rag.indexer import indexar_nota
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
        CRIAR_NOTA_PROMPT.format(
            mensagem=mensagem,
        )
    )

    try:
        dados = json.loads(
            limpar_resposta_json(resposta.content)
        )
    except (json.JSONDecodeError, TypeError):
        return None

    if not dados.get("deve_criar"):
        return None

    titulo = dados.get("titulo")
    conteudo = dados.get("conteudo")

    if not titulo or not conteudo:
        return {
            "resposta": (
                "Para criar uma nota, informe o título "
                "e o conteúdo."
            ),
            "fontes": [],
        }

    nota = Nota(
        titulo=titulo.strip(),
        conteudo=conteudo.strip(),
        usuario_id=usuario_id,
    )

    db.add(nota)

    try:
        db.commit()
        db.refresh(nota)

        vector_id = await indexar_nota(nota)

    except Exception:
        db.rollback()
        raise

    return {
        "resposta": f"Nota criada com sucesso: {nota.titulo}",
        "fontes": [
            {
                "nota_id": nota.id,
                "titulo": nota.titulo,
                "usuario_id": nota.usuario_id,
                # "vector_id": vector_id,
            }
        ],
    }
