from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_usuario_atual
from app.models.nota import Nota
from app.models.usuario import Usuario
from app.schemas.nota import NotaCreate, NotaAtualizar, NotaResponse
from app.rag.indexer import excluir_nota_indexada, indexar_nota


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

@router.patch(
    "/{nota_id}",
    response_model=NotaResponse,
)
async def atualizar_nota(
    nota_id: int,
    dados: NotaAtualizar,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_usuario_atual),
):
    nota = (
        db.query(Nota)
        .filter(
            Nota.id == nota_id,
            Nota.usuario_id == usuario_atual.id,
        )
        .first()
    )

    if nota is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nota não encontrada.",
        )

    dados_atualizacao = dados.model_dump(
        exclude_unset=True,
    )

    if not dados_atualizacao:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Informe ao menos um campo para atualização.",
        )

    titulo_anterior = nota.titulo
    conteudo_anterior = nota.conteudo

    if "titulo" in dados_atualizacao:
        nota.titulo = dados_atualizacao["titulo"].strip()

    if "conteudo" in dados_atualizacao:
        nota.conteudo = dados_atualizacao["conteudo"].strip()

    db.commit()
    db.refresh(nota)

    try:
        await indexar_nota(nota)

    except Exception as exc:
        nota.titulo = titulo_anterior
        nota.conteudo = conteudo_anterior

        db.commit()
        db.refresh(nota)

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Não foi possível sincronizar a nota "
                "com o banco vetorial."
            ),
        ) from exc

    return nota

@router.delete(
    "/{nota_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def excluir_nota(
    nota_id: int,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_usuario_atual),
):
    nota = (
        db.query(Nota)
        .filter(
            Nota.id == nota_id,
            Nota.usuario_id == usuario_atual.id,
        )
        .first()
    )

    if nota is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nota não encontrada.",
        )

    try:
        await excluir_nota_indexada(
            usuario_id=nota.usuario_id,
            nota_id=nota.id,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Não foi possível remover a nota "
                "do banco vetorial."
            ),
        ) from exc

    db.delete(nota)
    db.commit()

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )