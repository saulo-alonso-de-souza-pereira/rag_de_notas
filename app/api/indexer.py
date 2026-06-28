from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_usuario_atual
from app.models.usuario import Usuario
from app.services.indexer import indexar_notas_usuario


router = APIRouter(
    prefix="/indexer",
    tags=["indexer"],
)


@router.post("/notas")
def indexar_minhas_notas(
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_usuario_atual),
):
    total = indexar_notas_usuario(
        db=db,
        usuario_id=usuario_atual.id,
    )

    return {
        "status": "ok",
        "notas_indexadas": total,
    }