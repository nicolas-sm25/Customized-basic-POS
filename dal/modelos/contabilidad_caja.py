from sqlalchemy import Boolean, Column, Integer, Float, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from dal.modelos.base import Base

class ContabilidadCaja(Base):
    __tablename__ = 'contabilidad_caja'

    id = Column(Integer, primary_key=True, autoincrement=True)
    fecha_apertura = Column(DateTime, default=datetime.now)
    fecha_cierre = Column(DateTime, nullable=True)
    base_efectivo = Column(Float, default=0.0)
    abierta = Column(Boolean, default=True)
    
    ventas_efectivo = Column(Float, default=0.0)
    ventas_nequi = Column(Float, default=0.0)
    
    total_efectivo_cierre = Column(Float, nullable=True)
    diferencia = Column(Float, nullable=True)
    
    ventas = relationship("Venta", back_populates="caja")