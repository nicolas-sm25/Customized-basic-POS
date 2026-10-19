from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dal.modelos import Base

engine = create_engine(
    'sqlite:///tienda_local.db', 
    connect_args={'check_same_thread': False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def inicializar_base_datos():
    """Crea el archivo .db y todas las tablas si no existen."""
    Base.metadata.create_all(bind=engine)
    print("Base de datos inicializada: tablas creadas correctamente.")