import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dal.modelos import Base

carpeta_DB = "datos"
if not os.path.exists(carpeta_DB):
    os.makedirs(carpeta_DB)
    
ruta_DB = os.path.join(carpeta_DB, "productos_DB.db")

engine = create_engine(
    f'sqlite:///{ruta_DB}',
    connect_args={'check_same_thread': False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def inicializar_base_datos():
    """Crea el archivo .db y todas las tablas si no existen."""
    Base.metadata.create_all(bind=engine)
    print("Base de datos inicializada: tablas creadas correctamente.")