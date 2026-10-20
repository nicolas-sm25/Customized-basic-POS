import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from dal.modelos.base import Base
from dal.modelos.productos import Producto
from dal.modelos.ventas import Venta, DetalleVenta

CARPETA_BD = "datos"
if not os.path.exists(CARPETA_BD):
    os.makedirs(CARPETA_BD)

ruta_db = os.path.join(CARPETA_BD, "productos_DB.db")

engine = create_engine(
    f'sqlite:///{ruta_db}', 
    connect_args={'check_same_thread': False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def inicializar_base_datos():
    Base.metadata.create_all(bind=engine)
    print(f"Base de datos inicializada en la carpeta: {CARPETA_BD}/")
    
    
    

