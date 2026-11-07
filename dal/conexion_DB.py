import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dal.modelos.base import Base

# --- DETECCIÓN DE RUTA ABSOLUTA ---
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Ruta hacia 'datos'
CARPETA_DATOS = os.path.join(BASE_DIR, "datos")
CARPETA_CONFIG = os.path.join(CARPETA_DATOS, "configuraciones")
CARPETA_IMAGENES = os.path.join(CARPETA_DATOS, "imagenes")

# Carpeta exista junto al .exe o al script
if not os.path.exists(CARPETA_DATOS):
    os.makedirs(CARPETA_DATOS)

os.makedirs(CARPETA_CONFIG, exist_ok=True)
os.makedirs(CARPETA_IMAGENES, exist_ok=True)


# Ruta absoluta del archivo de la base de datos
RUTA_DB = os.path.join(CARPETA_CONFIG, "base_datos_tienda.db")

# Conexión a SQLite
SQLALCHEMY_DATABASE_URL = f"sqlite:///{RUTA_DB}"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def inicializar_base_datos():
    Base.metadata.create_all(bind=engine)