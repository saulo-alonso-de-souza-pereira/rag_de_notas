def test_deve_criar_usuario(client):
    response = client.post(
        "/usuarios",
        json={
            "nome": "Usuário Teste",
            "email": "teste@example.com",
            "senha": "senha123",
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert body["nome"] == "Usuário Teste"
    assert body["email"] == "teste@example.com"
    assert "senha" not in body
    assert "senha_hash" not in body

def test_nao_deve_criar_usuario_com_email_duplicado(client):
    payload = {
        "nome": "Usuário Teste",
        "email": "teste@example.com",
        "senha": "senha123",
    }

    primeira_resposta = client.post(
        "/usuarios",
        json=payload,
    )

    segunda_resposta = client.post(
        "/usuarios",
        json=payload,
    )

    assert primeira_resposta.status_code == 201
    assert segunda_resposta.status_code == 400
    assert segunda_resposta.json()["detail"] == "E-mail já cadastrado"