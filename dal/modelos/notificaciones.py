from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from dal.modelos.base import Base


class Notificacion(Base):
    __tablename__ = 'notificaciones'

    id = Column(Integer, primary_key=True, autoincrement=True)
    clave_unica = Column(String, unique=True, index=True, nullable=False)
    tipo = Column(String, nullable=False)           
    prioridad = Column(String, default="Media")     
    descripcion = Column(String, nullable=False)
    entidad_id = Column(Integer, nullable=True)     
    referencia_extra = Column(String, nullable=True)
    estado = Column(String, default="Activa", nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.now)
    ignorada_por = Column(String, nullable=True)
    fecha_ignorada = Column(DateTime, nullable=True)