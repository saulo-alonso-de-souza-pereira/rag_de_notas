import chainlit as cl

from chainlit_app.api_client import (
    ApiError,
    autenticar_usuario,
    perguntar_ao_rag,
)


@cl.password_auth_callback
async def auth_callback(
    username: str,
    password: str,
) -> cl.User | None:
    try:
        token = await autenticar_usuario(
            email=username,
            senha=password,
        )
    except ApiError:
        return None

    return cl.User(
        identifier=username,
        metadata={
            "token": token,
            "provider": "fastapi",
        },
    )


@cl.on_chat_start
async def on_chat_start() -> None:
    usuario = cl.user_session.get("user")

    if usuario is None:
        await cl.Message(
            content=(
                "Não foi possível identificar o usuário "
                "autenticado."
            )
        ).send()
        return

    token = usuario.metadata.get("token")

    if not token:
        await cl.Message(
            content=(
                "O token de autenticação não foi encontrado."
            )
        ).send()
        return

    cl.user_session.set("access_token", token)

    await cl.Message(
        content=(
            "Olá! Você pode criar notas, consultar suas "
            "anotações ou fazer perguntas gerais.\n\n"
            "Exemplos:\n"
            "- `Crie uma nota chamada Docker com o conteúdo ...`\n"
            "- `O que minhas notas dizem sobre Docker?`\n"
            "- `Explique o que é FastAPI.`"
        )
    ).send()


@cl.on_message
async def on_message(
    message: cl.Message,
) -> None:
    token = cl.user_session.get("access_token")

    if not token:
        await cl.Message(
            content=(
                "Sua sessão não possui um token válido. "
                "Entre novamente."
            )
        ).send()
        return

    resposta_ui = cl.Message(content="")
    await resposta_ui.send()

    try:
        resultado = await perguntar_ao_rag(
            pergunta=message.content,
            token=token,
        )
    except ApiError as exc:
        resposta_ui.content = (
            f"Não foi possível processar a solicitação: {exc}"
        )
        await resposta_ui.update()
        return

    resposta_ui.content = formatar_resposta(
        resposta=resultado.get(
            "resposta",
            "A API não retornou uma resposta.",
        ),
        fontes=resultado.get("fontes", []),
    )

    await resposta_ui.update()


def formatar_resposta(
    resposta: str,
    fontes: list[dict],
) -> str:
    if not fontes:
        return resposta

    linhas_fontes = []

    for fonte in fontes:
        nota_id = fonte.get("nota_id")
        titulo = fonte.get(
            "titulo",
            "Sem título",
        )
        score = fonte.get("score")

        linha = f"- Nota {nota_id}: {titulo}"

        if score is not None:
            linha += f" — relevância: {score:.2f}"

        linhas_fontes.append(linha)

    return (
        f"{resposta}\n\n"
        "### Fontes\n"
        + "\n".join(linhas_fontes)
    )
