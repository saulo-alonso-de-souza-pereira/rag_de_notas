from app.services.ollama import get_llm


async def responder_conversa_geral(mensagem: str) -> dict:
    llm = get_llm()

    resposta = await llm.ainvoke(mensagem)

    return {
        "resposta": resposta.content,
        "fontes": [],
    }
