from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def home():
    return {
        "mensagem": "API do RAG de Notas funcionando!"
    }