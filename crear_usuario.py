import sys
from dal.conexion_DB import SessionLocal
from dal.modelos.base import Base
from dal.modelos.usuarios import Usuario
from dal.modelos.contabilidad_caja import ContabilidadCaja
from dal.modelos.ventas import Venta
from dal.modelos.productos import Producto

def registrar_usuario(nombre, username, password, rol):
    sesion = SessionLocal()
    try:
        # Verificar si el nombre de usuario ya existe
        usuario_existente = sesion.query(Usuario).filter(Usuario.username == username).first()
        if usuario_existente:
            print(f"Error: El nombre de usuario '{username}' ya está en uso.")
            return

        # Validar rol
        rol_limpio = rol.capitalize()
        if rol_limpio not in ["Administrador", "Vendedor"]:
            print(f"Error: El rol '{rol}' no es válido. Debe ser 'Administrador' o 'Vendedor'.")
            return

        nuevo_usuario = Usuario(
            nombre=nombre,
            username=username,
            password=password,
            rol=rol_limpio
        )
        sesion.add(nuevo_usuario)
        sesion.commit()
        print(f"¡Usuario '{nombre}' registrado exitosamente!")
        print(f" - Usuario (Login): {username}")
        print(f" - Rol: {rol_limpio}")
    except Exception as e:
        sesion.rollback()
        print(f"Error inesperado al registrar el usuario: {e}")
    finally:
        sesion.close()

if __name__ == "__main__":
    if len(sys.argv) == 5:
        _, nombre, username, password, rol = sys.argv
        registrar_usuario(nombre, username, password, rol)
    else:
        print("💡 Uso del script de registro:")
        print("   py crear_usuario.py \"Nombre Apellido\" \"usuario\" \"contraseña\" \"Rol\"")