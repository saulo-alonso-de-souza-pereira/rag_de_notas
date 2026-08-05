import os
from typing import Any

import httpx


API_URL = os.getenv(
    "API_URL",
    "http://127.0.0.1:8000",
).rstrip("/")

REQUEST_TIMEOUT = 120.0


class ApiError(Exception):
    def __init__(
        self,
        message: str,
        status_code: int | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code


async def autenticar_usuario(
    email: str,
    senha: str,
) -> str:
    async with httpx.AsyncClient(
        timeout=REQUEST_TIMEOUT,
    ) as client:
        try:
            response = await client.post(
                f"{API_URL}/auth/login",
                data={
                    "username": email,
                    "password": senha,
                },
            )
        except httpx.RequestError as exc:
            raise ApiError(
                "Não foi possível conectar à API."
            ) from exc

    if response.status_code == 401:
        raise ApiError(
            "E-mail ou senha inválidos.",
            status_code=401,
        )

    if response.is_error:
        raise ApiError(
            obter_mensagem_erro(response),
            status_code=response.status_code,
        )

    body = response.json()
    token = body.get("access_token")

    if not token:
        raise ApiError(
            "A API não retornou um token de acesso."
        )

    return token


async def perguntar_ao_rag(
    pergunta: str,
    token: str,
) -> dict[str, Any]:
    async with httpx.AsyncClient(
        timeout=REQUEST_TIMEOUT,
    ) as client:
        try:
            response = await client.post(
                f"{API_URL}/rag/perguntar",
                headers={
                    "Authorization": f"Bearer {token}",
                },
                json={
                    "pergunta": pergunta,
                },
            )
        except httpx.RequestError as exc:
            raise ApiError(
                "Não foi possível conectar à API."
            ) from exc

    if response.status_code == 401:
        raise ApiError(
            "Sua autenticação expirou. Entre novamente.",
            status_code=401,
        )

    if response.is_error:
        raise ApiError(
            obter_mensagem_erro(response),
            status_code=response.status_code,
        )

    return response.json()


def obter_mensagem_erro(
    response: httpx.Response,
) -> str:
    try:
        body = response.json()
    except ValueError:
        return (
            f"A API retornou um erro "
            f"HTTP {response.status_code}."
        )

    detail = body.get("detail")

    if isinstance(detail, str):
        return detail

    return (
        f"A API retornou um erro "
        f"HTTP {response.status_code}."
    )
