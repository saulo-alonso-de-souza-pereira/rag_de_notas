from pydantic import BaseModel


class ChatRequest(BaseModel):
    mensagem: str


class ChatResponse(BaseModel):
    resposta: str


class RagPerguntaRequest(BaseModel):
    pergunta: str


class RagPerguntaResponse(BaseModel):
    resposta: str
    fontes: list[dict]