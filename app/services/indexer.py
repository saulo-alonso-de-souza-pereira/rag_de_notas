from langchain_core.documents import Document
from sqlalchemy.orm import Session

from app.models.nota import Nota
from app.services.qdrant import create_vector_store_from_documents


def indexar_notas_usuario(db: Session, usuario_id: int) -> int:
    notas = db.query(Nota).filter(
        Nota.usuario_id == usuario_id
    ).all()

    if not notas:
        return 0

    documentos = [
        Document(
            page_content=f"Título: {nota.titulo}\nConteúdo: {nota.conteudo}",
            metadata={
                "nota_id": nota.id,
                "usuario_id": nota.usuario_id,
                "titulo": nota.titulo,
            },
        )
        for nota in notas
    ]

    create_vector_store_from_documents(documentos)

    return len(documentos)