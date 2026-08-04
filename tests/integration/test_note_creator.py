from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.nota import Nota
from app.rag.note_creator import (
    tentar_criar_nota_por_linguagem_natural,
)


from app.core.security import gerar_hash_senha
from app.models.usuario import Usuario


usuario = Usuario(
    nome="Usuário Teste",
    email="teste@example.com",
    senha_hash=gerar_hash_senha("senha123"),
)

db_session.add(usuario)
db_session.commit()
db_session.refresh(usuario)

@pytest.mark.asyncio
async def test_deve_salvar_nota_no_sqlite(
    db_session,
    monkeypatch,
):
    resposta_llm = MagicMock()
    resposta_llm.content = """
    {
      "deve_criar": true,
      "titulo": "Docker",
      "conteudo": "Docker executa contêineres."
    }
    """

    llm_mock = MagicMock()
    llm_mock.ainvoke = AsyncMock(
        return_value=resposta_llm
    )

    monkeypatch.setattr(
        "app.rag.note_creator.get_llm",
        lambda: llm_mock,
    )

    indexar_mock = AsyncMock(
        return_value="uuid-vetorial"
    )

    monkeypatch.setattr(
        "app.rag.note_creator.indexar_nota",
        indexar_mock,
    )

    resultado = (
        await tentar_criar_nota_por_linguagem_natural(
            db=db_session,
            usuario_id=usuario.id,
            mensagem=(
                "Crie uma nota chamada Docker com o conteúdo "
                "Docker executa contêineres."
            ),
        )
    )

    nota = db_session.query(Nota).first()

    assert nota is not None
    assert nota.titulo == "Docker"
    assert nota.conteudo == "Docker executa contêineres."
    assert nota.usuario_id == 1

    assert resultado["resposta"] == (
        "Nota criada com sucesso: Docker"
    )

    indexar_mock.assert_awaited_once()