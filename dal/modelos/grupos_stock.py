from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from dal.modelos.base import Base


class GrupoStock(Base):
    __tablename__ = 'grupos_stock'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String, nullable=False)

    productos = relationship("Producto", back_populates="grupo_stock")