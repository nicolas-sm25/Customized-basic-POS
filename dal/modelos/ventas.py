from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from dal.modelos.base import Base
from dal.modelos.productos import Producto

class Venta(Base):
    __tablename__ = 'ventas'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    caja_id = Column(Integer, ForeignKey('contabilidad_caja.id'), nullable=True)
    fecha_hora = Column(DateTime, default=datetime.now)
    pagado = Column(Boolean, default=False)
    metodo_pago = Column(String, default="Efectivo", nullable=True)
    referencia = Column(String, nullable=True)
    total = Column(Float, default=0.0)
    ganancia_total = Column(Float, default=0.0)
    
    detalles = relationship("DetalleVenta", back_populates="venta", cascade="all, delete-orphan")
    caja = relationship("ContabilidadCaja", back_populates="ventas")

class DetalleVenta(Base):
    __tablename__ = 'detalles_venta'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    venta_id = Column(Integer, ForeignKey('ventas.id'), nullable=False)
    producto_id = Column(Integer, ForeignKey('productos.id'), nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(Float, nullable=False)
    costo_unitario = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)

    venta = relationship("Venta", back_populates="detalles")
    producto = relationship("Producto")