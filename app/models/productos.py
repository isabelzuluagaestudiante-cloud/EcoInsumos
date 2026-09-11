from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database.database import Base

class Producto(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150), nullable=False)
    descripcion = Column(Text, nullable=True)
    precio = Column(Integer, nullable=False, default=0)
    tipo_publicacion = Column(String(30), nullable=False, default="precio")
    imagen_url = Column(String(255), nullable=True)
    categoria_id = Column(Integer, ForeignKey("categorias.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    estado = Column(String(50), default="Disponible", nullable=False)

    categoria = relationship("Categoria", back_populates="productos")
    usuario = relationship("Usuario", back_populates="productos")
    carritos = relationship("Carrito", back_populates="producto")
    mensajes = relationship("Mensaje", back_populates="producto")