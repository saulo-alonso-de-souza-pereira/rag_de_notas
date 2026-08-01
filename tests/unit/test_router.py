from unittest.mock import AsyncMock, MagicMock

import pytest

from app.rag.router import classificar_intencao


@pytest.mark.asyncio
async def test_deve_classificar_criacao_de_nota(monkeypatch):
    llm_mock = MagicMock()
    llm_mock.ainvoke = AsyncMock()

    resposta_mock = MagicMock()
    resposta_mock.content = '{"intencao": "criar_nota"}'

    llm_mock.ainvoke.return_value = resposta_mock

    monkeypatch.setattr(
        "app.rag.router.get_llm",
        lambda: llm_mock,
    )

    resultado = await classificar_intencao(
        "Crie uma nota sobre Docker."
    )

    assert resultado == "criar_nota"

@pytest.mark.asyncio
async def test_deve_classificar_consulta_de_notas(monkeypatch):
    llm_mock = MagicMock()
    llm_mock.ainvoke = AsyncMock()

    resposta_mock = MagicMock()
    resposta_mock.content = '{"intencao": "consultar_notas"}'

    llm_mock.ainvoke.return_value = resposta_mock

    monkeypatch.setattr(
        "app.rag.router.get_llm",
        lambda: llm_mock,
    )

    resultado = await classificar_intencao(
        "O que minhas notas dizem sobre Docker?"
    )

    assert resultado == "consultar_notas"


@pytest.mark.asyncio
async def test_deve_classificar_conversa_geral(monkeypatch):
    llm_mock = MagicMock()
    llm_mock.ainvoke = AsyncMock()

    resposta_mock = MagicMock()
    resposta_mock.content = '{"intencao": "conversa_geral"}'

    llm_mock.ainvoke.return_value = resposta_mock

    monkeypatch.setattr(
        "app.rag.router.get_llm",
        lambda: llm_mock,
    )

    resultado = await classificar_intencao(
        "O que é Docker?"
    )

    assert resultado == "conversa_geral"

@pytest.mark.asyncio
async def test_deve_usar_fallback_quando_modelo_retornar_json_invalido(
    monkeypatch,
):
    llm_mock = MagicMock()
    llm_mock.ainvoke = AsyncMock()

    resposta_mock = MagicMock()
    resposta_mock.content = "resposta inválida"

    llm_mock.ainvoke.return_value = resposta_mock

    monkeypatch.setattr(
        "app.rag.router.get_llm",
        lambda: llm_mock,
    )

    resultado = await classificar_intencao(
        "Mensagem qualquer"
    )

    assert resultado == "consultar_notas"
