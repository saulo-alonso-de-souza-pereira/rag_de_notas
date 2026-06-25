from fastapi import APIRouter

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.ollama import get_llm


router = APIRouter(
    prefix="/chat",
    tags=["chat"],
)


@router.post("", response_model=ChatResponse)
async def conversar(dados: ChatRequest):
    llm = get_llm()

    resposta = await llm.ainvoke(dados.mensagem)

    return ChatResponse(
        resposta=resposta.content
    )