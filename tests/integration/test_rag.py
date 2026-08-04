from unittest.mock import AsyncMock

from app.models.nota import Nota


def test_deve_criar_nota_por_linguagem_natural(
    client,
    auth_headers,
    db_session,
    monkeypatch,
):
    monkeypatch.setattr(
        "app.api.rag.classificar_intencao",
        AsyncMock(return_value="criar_nota"),
    )

    resultado_criacao = {
        "resposta": "Nota criada com sucesso: Docker",
        "fontes": [
            {
                "nota_id": 1,
                "titulo": "Docker",
                "usuario_id": 1,
            }
        ],
    }

    criar_nota_mock = AsyncMock(
        return_value=resultado_criacao
    )

    monkeypatch.setattr(
        "app.api.rag.tentar_criar_nota_por_linguagem_natural",
        criar_nota_mock,
    )

    response = client.post(
        "/rag/perguntar",
        headers=auth_headers,
        json={
            "pergunta": (
                "Crie uma nota chamada Docker com o conteúdo "
                "Docker executa contêineres."
            )
        },
    )

    assert response.status_code == 200
    assert response.json() == resultado_criacao

    criar_nota_mock.assert_awaited_once()

def test_deve_consultar_notas_com_rag(
    client,
    auth_headers,
    monkeypatch,
):
    monkeypatch.setattr(
        "app.api.rag.classificar_intencao",
        AsyncMock(return_value="consultar_notas"),
    )

    resultado_rag = {
        "resposta": (
            "Segundo suas notas, Docker executa contêineres."
        ),
        "fontes": [
            {
                "nota_id": 1,
                "titulo": "Docker",
                "usuario_id": 1,
                "score": 0.91,
            }
        ],
    }

    rag_mock = AsyncMock(
        return_value=resultado_rag
    )

    monkeypatch.setattr(
        "app.api.rag.responder_pergunta_com_rag",
        rag_mock,
    )

    response = client.post(
        "/rag/perguntar",
        headers=auth_headers,
        json={
            "pergunta": (
                "O que minhas notas dizem sobre Docker?"
            )
        },
    )

    assert response.status_code == 200
    assert response.json() == resultado_rag

    rag_mock.assert_awaited_once_with(
        pergunta="O que minhas notas dizem sobre Docker?",
        usuario_id=1,
    )

def test_deve_responder_conversa_geral(
    client,
    auth_headers,
    monkeypatch,
):
    monkeypatch.setattr(
        "app.api.rag.classificar_intencao",
        AsyncMock(return_value="conversa_geral"),
    )

    resultado_geral = {
        "resposta": (
            "Docker é uma plataforma para executar contêineres."
        ),
        "fontes": [],
    }

    conversa_mock = AsyncMock(
        return_value=resultado_geral
    )

    monkeypatch.setattr(
        "app.api.rag.responder_conversa_geral",
        conversa_mock,
    )

    response = client.post(
        "/rag/perguntar",
        headers=auth_headers,
        json={
            "pergunta": "O que é Docker?"
        },
    )

    assert response.status_code == 200
    assert response.json() == resultado_geral

    conversa_mock.assert_awaited_once_with(
        mensagem="O que é Docker?",
    )

def test_nao_deve_acessar_rag_sem_autenticacao(client):
    response = client.post(
        "/rag/perguntar",
        json={
            "pergunta": "O que minhas notas dizem?"
        },
    )

    assert response.status_code == 401

def test_deve_informar_quando_nao_conseguir_extrair_nota(
    client,
    auth_headers,
    monkeypatch,
):
    monkeypatch.setattr(
        "app.api.rag.classificar_intencao",
        AsyncMock(return_value="criar_nota"),
    )

    monkeypatch.setattr(
        "app.api.rag.tentar_criar_nota_por_linguagem_natural",
        AsyncMock(return_value=None),
    )

    response = client.post(
        "/rag/perguntar",
        headers=auth_headers,
        json={
            "pergunta": "Crie uma nota."
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "resposta": (
            "Não consegui identificar título e conteúdo "
            "para criar a nota."
        ),
        "fontes": [],
    }
