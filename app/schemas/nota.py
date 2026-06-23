from pydantic import BaseModel


class NotaCreate(BaseModel):
    titulo: str
    conteudo: str


class NotaResponse(BaseModel):
    id: int
    titulo: str
    conteudo: str
    usuario_id: int

    model_config = {
        "from_attributes": True
    }