def test_deve_autenticar_usuario(client, usuario_criado):
    response = client.post(
        "/auth/login",
        data={
            "username": usuario_criado["email"],
            "password": usuario_criado["senha"],
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["token_type"] == "bearer"
    assert body["access_token"]


def test_nao_deve_autenticar_com_senha_incorreta(
    client,
    usuario_criado,
):
    response = client.post(
        "/auth/login",
        data={
            "username": usuario_criado["email"],
            "password": "senha-errada",
        },
    )

    assert response.status_code == 401
