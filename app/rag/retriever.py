from app.rag.vector_store import get_vector_store


async def buscar_documentos_relevantes(
    pergunta: str,
    usuario_id: int,
    k: int = 5,
):
    vector_store = get_vector_store()

    documentos = await vector_store.asimilarity_search(
        query=pergunta,
        k=k,
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

    return documentos