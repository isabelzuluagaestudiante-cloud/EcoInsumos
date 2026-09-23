from sqlalchemy import Boolean, Column, Integer, String

from app.database.database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)

    nombre = Column(
        String(100),
        nullable=False
    )

    email = Column(
        String(150),
        unique=True,
        nullable=False,
        index=True
    )

    password = Column(
        String(255),
        nullable=False
    )

    rol = Column(
        String(20),
        nullable=False,
        default="usuario"
    )

    activo = Column(
        Boolean,
        nullable=False,
        default=True
    )