from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.security import gerar_hash_senha
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate, UsuarioResponse


router = APIRouter(
    prefix="/usuarios",
    tags=["usuarios"],
)


@router.post(
    "",
    response_model=UsuarioResponse,
    status_code=status.HTTP_201_CREATED,
)
def criar_usuario(
    dados: UsuarioCreate,
    db: Session = Depends(get_db),
):
    usuario_existente = db.query(Usuario).filter(
        Usuario.email == dados.email
    ).first()

    if usuario_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="E-mail já cadastrado",
        )

    usuario = Usuario(
        nome=dados.nome,
        email=dados.email,
        senha_hash=gerar_hash_senha(dados.senha),
    )

    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    return usuario