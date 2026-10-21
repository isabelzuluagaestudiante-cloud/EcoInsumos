from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.database.database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    # Dato privado: no se muestra en ningún listado público.
    whatsapp = Column(String(20), nullable=False)
    rol = Column(String(50), default="usuario", nullable=False)
    activo = Column(Boolean, default=True)

    carritos = relationship("Carrito", back_populates="usuario")
    compras = relationship("Compra", foreign_keys="Compra.comprador_id", back_populates="comprador")
    productos_publicados = relationship("Producto", back_populates="vendedor")
    mensajes_enviados = relationship("Mensaje", foreign_keys="Mensaje.remitente_id", back_populates="remitente")
    mensajes_recibidos = relationship("Mensaje", foreign_keys="Mensaje.destinatario_id", back_populates="destinatario")
