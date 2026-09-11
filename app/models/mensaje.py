from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship

from app.database.database import Base


class Mensaje(Base):
    __tablename__ = "mensajes"

    id = Column(Integer, primary_key=True, index=True)
    contenido = Column(Text, nullable=False)
    remitente_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    destinatario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    creado_en = Column(DateTime, default=datetime.utcnow, nullable=False)

    remitente = relationship("Usuario", foreign_keys=[remitente_id], back_populates="mensajes_enviados")
    destinatario = relationship("Usuario", foreign_keys=[destinatario_id], back_populates="mensajes_recibidos")
    producto = relationship("Producto", back_populates="mensajes")
