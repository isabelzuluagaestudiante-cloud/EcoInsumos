from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database.database import Base


class Mensaje(Base):
    __tablename__ = "mensajes"

    id = Column(Integer, primary_key=True, index=True)
    contenido = Column(Text, nullable=False)
    remitente_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    destinatario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    tipo_solicitud = Column(String(30), default="mensaje", nullable=False)
    estado = Column(String(30), default="pendiente", nullable=False)
    oferta_imagen_url = Column(String(255), nullable=True)
    creado_en = Column(DateTime, default=datetime.utcnow, nullable=False)

    remitente = relationship("Usuario", foreign_keys=[remitente_id], back_populates="mensajes_enviados")
    destinatario = relationship("Usuario", foreign_keys=[destinatario_id], back_populates="mensajes_recibidos")
    producto = relationship("Producto", back_populates="mensajes")
