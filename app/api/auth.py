from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.security import criar_token_acesso, verificar_senha
from app.models.usuario import Usuario


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    usuario = db.query(Usuario).filter(
        Usuario.email == form_data.username
    ).first()

    if not usuario or not verificar_senha(
        form_data.password,
        usuario.senha_hash,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha inválidos",
        )

    access_token = criar_token_acesso(
        data={"sub": usuario.email}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }