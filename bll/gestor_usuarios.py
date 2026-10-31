from dal.conexion_DB import SessionLocal
from dal.modelos.usuarios import Usuario

def verificar_credenciales(username, password):
    """Verifica usuario y contraseña, devuelve el diccionario del usuario si es correcto."""
    sesion = SessionLocal()
    try:
        user = sesion.query(Usuario).filter(Usuario.username == username, Usuario.password == password, Usuario.activo == True).first()
        if user:
            return {
                "id": user.id,
                "nombre": user.nombre,
                "username": user.username,
                "rol": user.rol
            }
        return None
    finally:
        sesion.close()

def inicializar_usuario_admin():
    """Crea un usuario administrador por defecto si la tabla está vacía."""
    sesion = SessionLocal()
    try:
        existe = sesion.query(Usuario).first()
        if not existe:
            admin_default = Usuario(
                nombre="Administrador",
                username="admin",
                password="123",
                rol="Administrador"
            )
            sesion.add(admin_default)
            sesion.commit()
    finally:
        sesion.close()
        