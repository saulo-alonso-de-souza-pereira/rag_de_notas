def test_deve_criar_nota(
    client,
    auth_headers,
):
    response = client.post(
        "/notas",
        headers=auth_headers,
        json={
            "titulo": "Nota de teste",
            "conteudo": "Conteúdo da nota de teste.",
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert body["titulo"] == "Nota de teste"
    assert body["conteudo"] == "Conteúdo da nota de teste."
    assert body["usuario_id"] == 1


def test_nao_deve_criar_nota_sem_autenticacao(client):
    response = client.post(
        "/notas",
        json={
            "titulo": "Nota não autorizada",
            "conteudo": "Conteúdo",
        },
    )

    assert response.status_code == 401