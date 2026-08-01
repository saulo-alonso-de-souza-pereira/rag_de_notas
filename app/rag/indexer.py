from uuid import NAMESPACE_URL, uuid5

from langchain_core.documents import Document
from sqlalchemy.orm import Session

from app.models.nota import Nota
from app.rag.vector_store import get_vector_store


def gerar_id_vetorial(usuario_id: int, nota_id: int) -> str:
    identificador = f"usuario:{usuario_id}:nota:{nota_id}"

    return str(
        uuid5(
            NAMESPACE_URL,
            identificador,
        )
    )


def converter_nota_em_documento(nota: Nota) -> Document:
    return Document(
        page_content=(
            f"Título: {nota.titulo}\n"
            f"Conteúdo: {nota.conteudo}"
        ),
        metadata={
            "nota_id": nota.id,
            "usuario_id": nota.usuario_id,
            "titulo": nota.titulo,
        },
    )


async def indexar_nota(nota: Nota) -> str:
   
    vector_store = get_vector_store()

    documento = converter_nota_em_documento(nota)
    vector_id = gerar_id_vetorial(
        usuario_id=nota.usuario_id,
        nota_id=nota.id,
    )

    await vector_store.aadd_documents(
        documents=[documento],
        ids=[vector_id],
    )

    return vector_id


async def indexar_notas_usuario(
    db: Session,
    usuario_id: int,
) -> int:
    notas = (
        db.query(Nota)
        .filter(Nota.usuario_id == usuario_id)
        .all()
    )

    if not notas:
        return 0

    documentos = [
        converter_nota_em_documento(nota)
        for nota in notas
    ]

    ids = [
        gerar_id_vetorial(
            usuario_id=nota.usuario_id,
            nota_id=nota.id,
        )
        for nota in notas
    ]

    vector_store = get_vector_store()

    await vector_store.aadd_documents(
        documents=documentos,
        ids=ids,
    )

    return len(documentos)

async def excluir_nota_indexada(
    usuario_id: int,
    nota_id: int,
) -> bool:
    vector_store = get_vector_store()

    vector_id = gerar_id_vetorial(
        usuario_id=usuario_id,
        nota_id=nota_id,
    )

    resultado = await vector_store.adelete(
        ids=[vector_id],
    )

    return bool(resultado)
