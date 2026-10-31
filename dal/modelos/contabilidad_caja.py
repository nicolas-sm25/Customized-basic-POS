from sqlalchemy import Boolean, Column, Integer, Float, DateTime, String, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from dal.modelos.base import Base

class ContabilidadCaja(Base):
    __tablename__ = 'contabilidad_caja'

    id = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'), nullable=True)
    fecha_apertura = Column(DateTime, default=datetime.now)
    fecha_cierre = Column(DateTime, nullable=True)
    base_efectivo = Column(Float, default=0.0)
    abierta = Column(Boolean, default=True)
    
    ventas_efectivo = Column(Float, default=0.0)
    ventas_nequi = Column(Float, default=0.0)
    gastos_totales = Column(Float, default=0.0)
    
    costos_totales = Column(Float, default=0.0)
    ganancia_total = Column(Float, default=0.0)
    
    total_efectivo_cierre = Column(Float, nullable=True)
    diferencia = Column(Float, nullable=True)
    
    ventas = relationship("Venta", back_populates="caja")
    gastos = relationship("GastoCaja", back_populates="caja", cascade="all, delete-orphan")
    usuario = relationship("Usuario")

class GastoCaja(Base):
    __tablename__ = 'gastos_caja'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    caja_id = Column(Integer, ForeignKey('contabilidad_caja.id'), nullable=False)
    descripcion = Column(String, nullable=False)
    monto = Column(Float, nullable=False)
    fecha_hora = Column(DateTime, default=datetime.now)
    
    caja = relationship("ContabilidadCaja", back_populates="gastos")