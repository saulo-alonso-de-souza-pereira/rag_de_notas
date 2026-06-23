from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.core.database import Base


class Usuario(Base):

    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True)

    nome: Mapped[str] = mapped_column(String(100))

    email: Mapped[str] = mapped_column(
        String(120),
        unique=True
    )

    senha: Mapped[str] = mapped_column(String(255))