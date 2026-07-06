from langchain_core.documents import Document

from app.rag.prompt import RAG_PROMPT
from app.rag.retriever import buscar_documentos_relevantes
from app.services.ollama import get_llm


def formatar_contexto(documentos: list[Document]) -> str:
    partes = []

    for doc in documentos:
        nota_id = doc.metadata.get("nota_id")
        titulo = doc.metadata.get("titulo", "Sem título")

        partes.append(
            f"[Nota {nota_id} - {titulo}]\n{doc.page_content}"
        )

    return "\n\n".join(partes)


def montar_fontes(documentos: list[Document]) -> list[dict]:
    return [
        {
            "nota_id": doc.metadata.get("nota_id"),
            "titulo": doc.metadata.get("titulo"),
            "usuario_id": doc.metadata.get("usuario_id"),
        }
        for doc in documentos
    ]


async def responder_pergunta_com_rag(
    pergunta: str,
    usuario_id: int,
) -> dict:
    documentos = await buscar_documentos_relevantes(
        pergunta=pergunta,
        usuario_id=usuario_id,
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