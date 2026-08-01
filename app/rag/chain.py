from langchain_core.documents import Document

from app.rag.prompt import RAG_PROMPT
from app.rag.retriever import (
    DocumentoRecuperado,
    buscar_documentos_relevantes,
)
from app.services.ollama import get_llm


def criar_chain_rag():
    return RAG_PROMPT | get_llm()

def formatar_contexto(
    resultados: list[DocumentoRecuperado],
) -> str:
    partes = []

    for resultado in resultados:
        doc = resultado.documento

        nota_id = doc.metadata.get("nota_id")
        titulo = doc.metadata.get("titulo", "Sem título")

        partes.append(
            f"[Nota {nota_id} - {titulo}]\n"
            f"{doc.page_content}"
        )

    return "\n\n".join(partes)


def montar_fontes(
    resultados: list[DocumentoRecuperado],
) -> list[dict]:
    return [
        {
            "nota_id": resultado.documento.metadata.get("nota_id"),
            "titulo": resultado.documento.metadata.get("titulo"),
            "usuario_id": resultado.documento.metadata.get(
                "usuario_id"
            ),
            "score": round(resultado.score, 4),
        }
        for resultado in resultados
    ]


async def responder_pergunta_com_rag(
    pergunta: str,
    usuario_id: int,
) -> dict:
    resultados = await buscar_documentos_relevantes(
        pergunta=pergunta,
        usuario_id=usuario_id,
    )

    if not resultados:
        return {
            "resposta": (
                "Não encontrei informações suficientemente "
                "relevantes nas suas notas."
            ),
            "fontes": [],
        }

    chain = criar_chain_rag()

    resposta = await chain.ainvoke(
        {
            "context": formatar_contexto(resultados),
            "question": pergunta,
        }
    )

    return {
        "resposta": resposta.content,
        "fontes": montar_fontes(resultados),
    }