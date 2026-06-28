from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.nota import Nota
from app.prompts.rag_prompt import RAG_PROMPT
from app.services.ollama import get_llm
from app.services.qdrant import get_vector_store


def formatar_contexto(documentos) -> str:
    if not documentos:
        return ""

    partes = []

    for doc in documentos:
        titulo = doc.metadata.get("titulo", "Sem título")
        nota_id = doc.metadata.get("nota_id", "sem_id")

        partes.append(
            f"[Nota {nota_id} - {titulo}]\n{doc.page_content}"
        )

    return "\n\n".join(partes)


def montar_fontes(documentos) -> list[dict]:
    fontes = []

    for doc in documentos:
        fontes.append(
            {
                "nota_id": doc.metadata.get("nota_id"),
                "titulo": doc.metadata.get("titulo"),
                "usuario_id": doc.metadata.get("usuario_id"),
            }
        )

    return fontes


async def responder_com_rag(
    db: Session,
    usuario_id: int,
    pergunta: str,
) -> dict:
    total_notas = db.query(Nota).filter(
        Nota.usuario_id == usuario_id
    ).count()

    if total_notas == 0:
        return {
            "resposta": "Você ainda não possui notas cadastradas.",
            "fontes": [],
        }

    vector_store = get_vector_store()

    documentos = await vector_store.asimilarity_search(
        query=pergunta,
        k=5,
        filter={
            "must": [
                {
                    "key": "metadata.usuario_id",
                    "match": {
                        "value": usuario_id,
                    },
                }
            ]
        },
    )

    if not documentos:
        return {
            "resposta": "Não encontrei essa informação nas suas notas.",
            "fontes": [],
        }

    contexto = formatar_contexto(documentos)

    chain = RAG_PROMPT | get_llm()

    resposta = await chain.ainvoke(
        {
            "context": contexto,
            "question": pergunta,
        }
    )

    return {
        "resposta": resposta.content,
        "fontes": montar_fontes(documentos),
    }