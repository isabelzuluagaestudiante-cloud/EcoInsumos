from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from app.database.database import Base

class Categoria(Base):
    __tablename__ = "categorias"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), unique=True, nullable=False)
    descripcion = Column(Text, nullable=True)

    productos = relationship("Producto", back_populates="categoria")