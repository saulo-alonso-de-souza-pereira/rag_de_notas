from uuid import UUID
from types import SimpleNamespace

from app.rag.indexer import (
    gerar_id_vetorial,
    indexar_nota,
    excluir_nota_indexada,
    converter_nota_em_documento,
)
from unittest.mock import AsyncMock, MagicMock

import pytest


def test_deve_gerar_id_vetorial_deterministico():
    primeiro_id = gerar_id_vetorial(
        usuario_id=1,
        nota_id=10,
    )

    segundo_id = gerar_id_vetorial(
        usuario_id=1,
        nota_id=10,
    )

    assert primeiro_id == segundo_id

    # Confirma que o valor retornado é um UUID válido.
    assert str(UUID(primeiro_id)) == primeiro_id


def test_deve_gerar_ids_diferentes_para_notas_diferentes():
    primeiro_id = gerar_id_vetorial(
        usuario_id=1,
        nota_id=10,
    )

    segundo_id = gerar_id_vetorial(
        usuario_id=1,
        nota_id=11,
    )

    assert primeiro_id != segundo_id


def test_deve_gerar_ids_diferentes_para_usuarios_diferentes():
    primeiro_id = gerar_id_vetorial(
        usuario_id=1,
        nota_id=10,
    )

    segundo_id = gerar_id_vetorial(
        usuario_id=2,
        nota_id=10,
    )

    assert primeiro_id != segundo_id

def test_deve_converter_nota_em_documento():
    nota = SimpleNamespace(
        id=10,
        titulo="Docker",
        conteudo="Docker executa contêineres.",
        usuario_id=1,
    )

    documento = converter_nota_em_documento(nota)

    assert documento.page_content == (
        "Título: Docker\n"
        "Conteúdo: Docker executa contêineres."
    )

    assert documento.metadata == {
        "nota_id": 10,
        "usuario_id": 1,
        "titulo": "Docker",
    }

@pytest.mark.asyncio
async def test_deve_indexar_uma_nota(monkeypatch):
    vector_store_mock = MagicMock()
    vector_store_mock.aadd_documents = AsyncMock(
        return_value=None
    )

    monkeypatch.setattr(
        "app.rag.indexer.get_vector_store",
        lambda: vector_store_mock,
    )

    nota = SimpleNamespace(
        id=10,
        titulo="Docker",
        conteudo="Docker executa contêineres.",
        usuario_id=1,
    )

    vector_id = await indexar_nota(nota)

    id_esperado = gerar_id_vetorial(
        usuario_id=1,
        nota_id=10,
    )

    assert vector_id == id_esperado

    vector_store_mock.aadd_documents.assert_awaited_once()

    chamada = (
        vector_store_mock
        .aadd_documents
        .await_args
    )

    assert chamada.kwargs["ids"] == [id_esperado]

    documentos = chamada.kwargs["documents"]

    assert len(documentos) == 1
    assert documentos[0].metadata["nota_id"] == 10
    assert documentos[0].metadata["usuario_id"] == 1

@pytest.mark.asyncio
async def test_deve_reutilizar_id_ao_reindexar_nota(
    monkeypatch,
):
    vector_store_mock = MagicMock()
    vector_store_mock.aadd_documents = AsyncMock(
        return_value=None
    )

    monkeypatch.setattr(
        "app.rag.indexer.get_vector_store",
        lambda: vector_store_mock,
    )

    nota = SimpleNamespace(
        id=10,
        titulo="Docker",
        conteudo="Primeiro conteúdo.",
        usuario_id=1,
    )

    primeiro_id = await indexar_nota(nota)

    nota.conteudo = "Conteúdo atualizado."

    segundo_id = await indexar_nota(nota)

    assert primeiro_id == segundo_id
    assert (
        vector_store_mock
        .aadd_documents
        .await_count
        == 2
    )

    primeira_chamada = (
        vector_store_mock
        .aadd_documents
        .await_args_list[0]
    )

    segunda_chamada = (
        vector_store_mock
        .aadd_documents
        .await_args_list[1]
    )

    assert primeira_chamada.kwargs["ids"] == [primeiro_id]
    assert segunda_chamada.kwargs["ids"] == [primeiro_id]

@pytest.mark.asyncio
async def test_deve_excluir_nota_indexada(monkeypatch):
    vector_store_mock = MagicMock()
    vector_store_mock.adelete = AsyncMock(
        return_value=True
    )

    monkeypatch.setattr(
        "app.rag.indexer.get_vector_store",
        lambda: vector_store_mock,
    )

    resultado = await excluir_nota_indexada(
        usuario_id=1,
        nota_id=10,
    )

    vector_id = gerar_id_vetorial(
        usuario_id=1,
        nota_id=10,
    )

    vector_store_mock.adelete.assert_awaited_once_with(
        ids=[vector_id],
    )

    assert resultado is True