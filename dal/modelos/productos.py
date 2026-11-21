from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from dal.modelos.base import Base
from dal.modelos.proveedores import Proveedor
from dal.modelos.grupos_stock import GrupoStock


class Producto(Base):
    __tablename__ = 'productos'

    id = Column(Integer, primary_key=True, autoincrement=True)
    codigo_barras = Column(String, unique=True, index=True, nullable=True)
    nombre = Column(String, nullable=False)
    costo = Column(Float, nullable=False)
    precio_venta = Column(Float, nullable=False)
    stock = Column(Integer, default=0)
    activo = Column(Boolean, default=True)
    es_paquete = Column(Boolean, default=False)
    producto_base_id = Column(Integer, ForeignKey('productos.id'), nullable=True)
    cantidad_por_paquete = Column(Integer, default=1)
    proveedor_id = Column(Integer, ForeignKey('proveedores.id'), nullable=True)
    grupo_stock_id = Column(Integer, ForeignKey('grupos_stock.id'), nullable=True)

    producto_base = relationship("Producto", remote_side=[id], backref="paquetes_asociados")
    proveedor = relationship("Proveedor", back_populates="productos")
    grupo_stock = relationship("GrupoStock", back_populates="productos")

    def __init__(self, nombre, costo, precio_venta, codigo_barras=None, stock=0, es_paquete=False, producto_base_id=None, cantidad_por_paquete=1, grupo_stock_id=None):
        self.nombre = nombre
        self.costo = costo
        self.precio_venta = precio_venta
        self.codigo_barras = codigo_barras
        self.stock = stock
        self.activo = True
        self.es_paquete = es_paquete
        self.producto_base_id = producto_base_id
        self.cantidad_por_paquete = cantidad_por_paquete
        self.grupo_stock_id = grupo_stock_id

    def __repr__(self):
        return f"<Producto(nombre='{self.nombre}', precio={self.precio_venta}, stock={self.stock}, paquete={self.es_paquete})>"