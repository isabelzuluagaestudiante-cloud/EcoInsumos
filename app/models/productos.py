from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database.database import Base

class Producto(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150), nullable=False)
    descripcion = Column(Text, nullable=True)
    precio = Column(Integer, nullable=False)
    es_intercambio = Column(Boolean, nullable=False, default=False)
    categoria_id = Column(Integer, ForeignKey("categorias.id"), nullable=False)
    vendedor_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    imagen = Column(String(255), nullable=True)
    disponible = Column(Boolean, nullable=False, default=True)

    categoria = relationship("Categoria", back_populates="productos")
    carritos = relationship("Carrito", back_populates="producto")
    vendedor = relationship("Usuario", back_populates="productos_publicados")
    compras = relationship("Compra", back_populates="producto")
    mensajes = relationship("Mensaje", back_populates="producto")
