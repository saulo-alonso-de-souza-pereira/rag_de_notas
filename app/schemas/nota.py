from pydantic import BaseModel, ConfigDict, Field


class NotaCreate(BaseModel):
    titulo: str
    conteudo: str


class NotaResponse(BaseModel):
    id: int
    titulo: str
    conteudo: str
    usuario_id: int

    model_config = ConfigDict(from_attributes=True)

class NotaAtualizar(BaseModel):
    titulo: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
    )
    conteudo: str | None = Field(
        default=None,
        min_length=1,
    )

