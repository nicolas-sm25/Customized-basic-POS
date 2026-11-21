from dal.conexion_DB import SessionLocal
from dal.modelos.usuarios import Usuario


def verificar_credenciales(username, password):
    """Verifica usuario y contraseña, devuelve el diccionario del usuario si es correcto."""
    sesion = SessionLocal()
    try:
        user = sesion.query(Usuario).filter(
            Usuario.username == username,
            Usuario.password == password,
            Usuario.activo == True
        ).first()
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


def hay_usuarios_registrados():
    """Retorna True si existe al menos un usuario en la base de datos."""
    sesion = SessionLocal()
    try:
        return sesion.query(Usuario).first() is not None
    finally:
        sesion.close()


def crear_usuario(nombre, username, password, rol="Administrador"):
    """Registra un nuevo usuario en la base de datos y retorna (exito, resultado_o_error)."""
    sesion = SessionLocal()
    try:
        existente = sesion.query(Usuario).filter(Usuario.username == username).first()
        if existente:
            return False, "Ese nombre de usuario ya está en uso."

        nuevo = Usuario(
            nombre=nombre,
            username=username,
            password=password,
            rol=rol
        )
        if getattr(nuevo, "activo", None) is None:
            nuevo.activo = True

        sesion.add(nuevo)
        sesion.commit()
        sesion.refresh(nuevo)

        return True, {
            "id": nuevo.id,
            "nombre": nuevo.nombre,
            "username": nuevo.username,
            "rol": nuevo.rol
        }
    except Exception as e:
        sesion.rollback()
        return False, f"Error al crear usuario: {str(e)}"
    finally:
        sesion.close()


def obtener_usuarios():
    sesion = SessionLocal()
    try:
        usuarios = sesion.query(Usuario).all()
        return [
            {
                "id": u.id,
                "nombre": u.nombre,
                "username": u.username,
                "rol": u.rol,
                "activo": u.activo
            }
            for u in usuarios
        ]
    finally:
        sesion.close()


def cambiar_estado_usuario(usuario_id, estado_nuevo):
    sesion = SessionLocal()
    try:
        user = sesion.query(Usuario).filter(Usuario.id == usuario_id).first()
        if not user:
            return False, "Usuario no encontrado."

        if not estado_nuevo:
            if user.id == 1 or user.username == "admin":
                return False, "Por seguridad, no se puede deshabilitar al administrador principal."

            if user.rol == "Administrador":
                admins_activos = sesion.query(Usuario).filter(
                    Usuario.rol == "Administrador",
                    Usuario.activo == True
                ).count()
                if admins_activos <= 1:
                    return False, "Debe quedar al menos un Administrador activo en el sistema."

        user.activo = estado_nuevo
        sesion.commit()
        return True, "Estado de usuario actualizado."
    finally:
        sesion.close()