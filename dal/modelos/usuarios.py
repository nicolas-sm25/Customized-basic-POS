from sqlalchemy import Column, Integer, String, Boolean
from dal.modelos.base import Base

class Usuario(Base):
    __tablename__ = 'usuarios'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String, nullable=False)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False) 
    rol = Column(String, nullable=False)      
    activo = Column(Boolean, default=True)

    def __init__(self, nombre, username, password, rol):
        self.nombre = nombre
        self.username = username
        self.password = password
        self.rol = rol
        self.activo = True