from unittest.mock import AsyncMock, MagicMock

import pytest
from langchain_core.documents import Document

from app.rag.chain import responder_pergunta_com_rag
from app.rag.retriever import DocumentoRecuperado


@pytest.mark.asyncio
async def test_deve_responder_com_fontes(monkeypatch):
    documento = Document(
        page_content="Docker executa contêineres.",
        metadata={
            "nota_id": 10,
            "titulo": "Docker",
            "usuario_id": 1,
        },
    )

    resultados = [
        DocumentoRecuperado(
            documento=documento,
            score=0.91,
        )
    ]

    monkeypatch.setattr(
        "app.rag.chain.buscar_documentos_relevantes",
        AsyncMock(return_value=resultados),
    )

    resposta_llm = MagicMock()
    resposta_llm.content = (
        "Docker é utilizado para executar contêineres."
    )

    chain_mock = MagicMock()
    chain_mock.ainvoke = AsyncMock(
        return_value=resposta_llm
    )

    prompt_mock = MagicMock()
    prompt_mock.__or__ = MagicMock(
        return_value=chain_mock
    )

    monkeypatch.setattr(
        "app.rag.chain.RAG_PROMPT",
        prompt_mock,
    )

    monkeypatch.setattr(
        "app.rag.chain.get_llm",
        lambda: MagicMock(),
    )

    monkeypatch.setattr(
        "app.rag.chain.criar_chain_rag",
        lambda: chain_mock,
    )

    resultado = await responder_pergunta_com_rag(
        pergunta="Para que serve o Docker?",
        usuario_id=1,
    )

    assert resultado["resposta"] == (
        "Docker é utilizado para executar contêineres."
    )

    assert resultado["fontes"] == [
        {
            "nota_id": 10,
            "titulo": "Docker",
            "usuario_id": 1,
            "score": 0.91,
        }
    ]

@pytest.mark.asyncio
async def test_deve_informar_quando_nao_encontrar_notas(
    monkeypatch,
):
    monkeypatch.setattr(
        "app.rag.chain.buscar_documentos_relevantes",
        AsyncMock(return_value=[]),
    )

    resultado = await responder_pergunta_com_rag(
        pergunta="Assunto desconhecido",
        usuario_id=1,
    )

    assert resultado == {
        "resposta": (
            "Não encontrei informações suficientemente "
            "relevantes nas suas notas."
        ),
        "fontes": [],
    }
