import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from dal.modelos.base import Base
from dal.modelos.productos import Producto
from dal.modelos.ventas import Venta, DetalleVenta

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CARPETA_BD = os.path.join(BASE_DIR, "datos")

if not os.path.exists(CARPETA_BD):
    os.makedirs(CARPETA_BD)

ruta_db = os.path.join(CARPETA_BD, "productos_DB.db")

db_url = f"sqlite:///{ruta_db.replace(chr(92), '/')}"

engine = create_engine(
    db_url, 
    connect_args={'check_same_thread': False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def inicializar_base_datos():
    Base.metadata.create_all(bind=engine)
    print(f"Base de datos asegurada en: {ruta_db}")