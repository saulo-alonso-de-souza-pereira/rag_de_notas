from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_usuario_atual
from app.models.nota import Nota
from app.models.usuario import Usuario
from app.schemas.nota import NotaCreate, NotaResponse


router = APIRouter(
    prefix="/notas",
    tags=["notas"],
)


@router.post(
    "",
    response_model=NotaResponse,
    status_code=status.HTTP_201_CREATED,
)
def criar_nota(
    dados: NotaCreate,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_usuario_atual),
):
    nota = Nota(
        titulo=dados.titulo,
        conteudo=dados.conteudo,
        usuario_id=usuario_atual.id,
    )

    db.add(nota)
    db.commit()
    db.refresh(nota)

    return nota


@router.get(
    "",
    response_model=list[NotaResponse],
)
def listar_notas(
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_usuario_atual),
):
    return db.query(Nota).filter(
        Nota.usuario_id == usuario_atual.id
    ).all()