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

def obtener_usuarios():
    sesion = SessionLocal()
    try:
        usuarios = sesion.query(Usuario).all()
        # Excluimos la contraseña por seguridad al enviarlo a la vista
        return [{"id": u.id, "nombre": u.nombre, "username": u.username, "rol": u.rol, "activo": u.activo} for u in usuarios]
    finally:
        sesion.close()

def cambiar_estado_usuario(usuario_id, estado_nuevo):
    sesion = SessionLocal()
    try:
        user = sesion.query(Usuario).filter(Usuario.id == usuario_id).first()
        if user:
            if user.username == "admin" and not estado_nuevo:
                return False, "Por seguridad, no se puede deshabilitar al admin principal."
            user.activo = estado_nuevo
            sesion.commit()
            return True, "Estado de usuario actualizado."
        return False, "Usuario no encontrado."
    finally:
        sesion.close()