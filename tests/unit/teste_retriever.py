from unittest.mock import AsyncMock, MagicMock

import pytest
from langchain_core.documents import Document

from app.rag.retriever import (
    buscar_documentos_relevantes,
)


@pytest.mark.asyncio
async def test_deve_retornar_documentos_com_score(
    monkeypatch,
):
    documento = Document(
        page_content="Docker executa contêineres.",
        metadata={
            "nota_id": 10,
            "usuario_id": 1,
            "titulo": "Docker",
        },
    )

    vector_store_mock = MagicMock()
    vector_store_mock.asimilarity_search_with_score = (
        AsyncMock(
            return_value=[
                (documento, 0.91),
            ]
        )
    )

    monkeypatch.setattr(
        "app.rag.retriever.get_vector_store",
        lambda: vector_store_mock,
    )

    resultados = await buscar_documentos_relevantes(
        pergunta="O que é Docker?",
        usuario_id=1,
        k=5,
        score_threshold=0.65,
    )

    assert len(resultados) == 1

    resultado = resultados[0]

    assert resultado.documento == documento
    assert resultado.score == 0.91

@pytest.mark.asyncio
async def test_deve_buscar_apenas_notas_do_usuario(
    monkeypatch,
):
    vector_store_mock = MagicMock()
    vector_store_mock.asimilarity_search_with_score = (
        AsyncMock(return_value=[])
    )

    monkeypatch.setattr(
        "app.rag.retriever.get_vector_store",
        lambda: vector_store_mock,
    )

    await buscar_documentos_relevantes(
        pergunta="Docker",
        usuario_id=7,
        k=3,
        score_threshold=0.70,
    )

    chamada = (
        vector_store_mock
        .asimilarity_search_with_score
        .await_args
    )

    assert chamada.kwargs["query"] == "Docker"
    assert chamada.kwargs["k"] == 3
    assert chamada.kwargs["score_threshold"] == 0.70

    filtro = chamada.kwargs["filter"]

    assert filtro.must[0].key == "metadata.usuario_id"
    assert filtro.must[0].match.value == 7

@pytest.mark.asyncio
async def test_deve_retornar_lista_vazia_sem_resultados(
    monkeypatch,
):
    vector_store_mock = MagicMock()
    vector_store_mock.asimilarity_search_with_score = (
        AsyncMock(return_value=[])
    )

    monkeypatch.setattr(
        "app.rag.retriever.get_vector_store",
        lambda: vector_store_mock,
    )

    resultados = await buscar_documentos_relevantes(
        pergunta="Assunto inexistente",
        usuario_id=1,
        k=5,
        score_threshold=0.80,
    )

    assert resultados == []
