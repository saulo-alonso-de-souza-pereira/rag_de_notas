from fastapi import FastAPI

from app.api import auth, chat, embeddings, indexer, notas, qdrant, usuarios
from app.core.database import Base, engine
from app.models import Nota, Usuario

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="RAG de Notas",
    version="1.0.0",
    description="API para gerenciamento de notas e consultas RAG utilizando LangChain e Ollama local.",
)


@app.get("/")
def home():
    return {
        "projeto": "RAG de Notas",
        "status": "online",
        "versao": "1.0.0",
        "ollama": "local",
    }


app.include_router(auth.router)
app.include_router(usuarios.router)
app.include_router(notas.router)
app.include_router(chat.router)
app.include_router(embeddings.router)
app.include_router(qdrant.router)
app.include_router(indexer.router)