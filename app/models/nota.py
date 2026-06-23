from sqlalchemy import ForeignKey
from sqlalchemy import Text
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.core.database import Base


class Nota(Base):

    __tablename__ = "notas"

    id: Mapped[int] = mapped_column(primary_key=True)

    titulo: Mapped[str]

    conteudo: Mapped[str] = mapped_column(Text)

    usuario_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id")
    )