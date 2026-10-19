from sqlalchemy import Column, Integer, String, Float, Boolean
from sqlalchemy.orm import declarative_base

Base = declarative_base()
class Producto(Base):
    
    __tablename__ = 'productos'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    codigo_barras = Column(String, unique=True, index=True, nullable=True)
    nombre = Column(String, nullable=False)
    costo = Column(Float, nullable=False)
    precio_venta = Column(Float, nullable=False)
    stock = Column(Integer, default=0)
    activo = Column(Boolean, default=True)


    def __init__(self, nombre, costo, precio_venta, codigo_barras=None, stock=0):
        self.nombre = nombre
        self.costo = costo
        self.precio_venta = precio_venta
        
        self.codigo_barras = codigo_barras
        self.stock = stock
        
        self.activo = True

    def __repr__(self):
        return f"<Producto(nombre='{self.nombre}', precio={self.precio_venta}, stock={self.stock})>"