from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from dal.modelos.base import Base


class Proveedor(Base):
    __tablename__ = 'proveedores'

    id = Column(Integer, primary_key=True, autoincrement=True)
    proveedor = Column(String, nullable=False)
    nombre_proveedor = Column(String, nullable=False)
    telefono = Column(String, nullable=True)
    nit = Column(String, nullable=True)

    productos = relationship("Producto", back_populates="proveedor")