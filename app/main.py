from fastapi import FastAPI

from app.api.routes import router

from app.core.database import engine

from app.db.base import Base


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="RAG de Notas",
    version="1.0.0"
)

app.include_router(router)