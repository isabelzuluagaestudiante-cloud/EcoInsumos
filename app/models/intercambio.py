from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database.database import Base


class SolicitudIntercambio(Base):
    __tablename__ = "solicitudes_intercambio"

    id = Column(Integer, primary_key=True, index=True)
    solicitante_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    producto_solicitado_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    producto_ofrecido_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    mensaje = Column(Text, nullable=True)
    estado = Column(String(20), nullable=False, default="pendiente")
    creada_en = Column(DateTime, nullable=False, default=datetime.utcnow)

    solicitante = relationship("Usuario", foreign_keys=[solicitante_id])
    producto_solicitado = relationship("Producto", foreign_keys=[producto_solicitado_id])
    producto_ofrecido = relationship("Producto", foreign_keys=[producto_ofrecido_id])
