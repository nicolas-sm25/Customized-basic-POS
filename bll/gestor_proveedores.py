from dal.conexion_DB import SessionLocal
from dal.modelos.proveedores import Proveedor
from dal.modelos.productos import Producto


def obtener_proveedores():
    """Retorna todos los proveedores registrados junto con la lista de sus productos asociados."""
    sesion = SessionLocal()
    try:
        proveedores = sesion.query(Proveedor).order_by(Proveedor.id.desc()).all()
        resultado = []
        for p in proveedores:
            prods_activos = [prod for prod in p.productos if prod.activo]
            nombres_prods = [prod.nombre for prod in prods_activos]
            resultado.append({
                "id": p.id,
                "proveedor": p.proveedor,
                "nombre_proveedor": p.nombre_proveedor,
                "telefono": p.telefono or "Sin teléfono",
                "nit": p.nit or "Sin NIT",
                "productos": nombres_prods,
                "cantidad_productos": len(nombres_prods)
            })
        return resultado
    finally:
        sesion.close()


def obtener_proveedor_por_id(proveedor_id):
    """Retorna los datos completos de un proveedor y los IDs de sus productos vinculados."""
    sesion = SessionLocal()
    try:
        p = sesion.query(Proveedor).filter(Proveedor.id == proveedor_id).first()
        if not p:
            return None
        return {
            "id": p.id,
            "proveedor": p.proveedor,
            "nombre_proveedor": p.nombre_proveedor,
            "telefono": p.telefono or "",
            "nit": p.nit or "",
            "ids_productos": [prod.id for prod in p.productos]
        }
    finally:
        sesion.close()


def obtener_productos_para_proveedor():
    """Devuelve los productos activos disponibles para vincular a un proveedor."""
    sesion = SessionLocal()
    try:
        productos = sesion.query(Producto).filter(Producto.activo == True).order_by(Producto.nombre.asc()).all()
        return [{
            "id": p.id,
            "nombre": p.nombre,
            "proveedor_id": p.proveedor_id,
            "proveedor_actual": p.proveedor.proveedor if p.proveedor else None
        } for p in productos]
    finally:
        sesion.close()


def agregar_proveedor(proveedor, nombre_proveedor, telefono="", nit="", ids_productos=None):
    """Crea un nuevo proveedor y le asigna los productos seleccionados."""
    if not proveedor.strip() or not nombre_proveedor.strip():
        return False, "Los campos 'Proveedor' y 'Nombre del Proveedor' son obligatorios."

    sesion = SessionLocal()
    try:
        if nit.strip():
            existente = sesion.query(Proveedor).filter(Proveedor.nit == nit.strip()).first()
            if existente:
                return False, f"Ya existe un proveedor registrado con el NIT {nit.strip()}."

        nuevo = Proveedor(
            proveedor=proveedor.strip(),
            nombre_proveedor=nombre_proveedor.strip(),
            telefono=telefono.strip() if telefono.strip() else None,
            nit=nit.strip() if nit.strip() else None
        )
        sesion.add(nuevo)
        sesion.flush()

        if ids_productos:
            productos_db = sesion.query(Producto).filter(Producto.id.in_(ids_productos)).all()
            for prod in productos_db:
                prod.proveedor_id = nuevo.id

        sesion.commit()
        return True, f"Proveedor '{nuevo.proveedor}' registrado exitosamente."
    except Exception as e:
        sesion.rollback()
        return False, f"Error al guardar proveedor: {str(e)}"
    finally:
        sesion.close()


def actualizar_proveedor(proveedor_id, proveedor, nombre_proveedor, telefono="", nit="", ids_productos=None):
    """Actualiza los datos de un proveedor y sincroniza sus productos vinculados."""
    if not proveedor.strip() or not nombre_proveedor.strip():
        return False, "Los campos 'Proveedor' y 'Nombre del Proveedor' son obligatorios."

    sesion = SessionLocal()
    try:
        prov_db = sesion.query(Proveedor).filter(Proveedor.id == proveedor_id).first()
        if not prov_db:
            return False, "Proveedor no encontrado."

        if nit.strip():
            duplicado = sesion.query(Proveedor).filter(
                Proveedor.nit == nit.strip(),
                Proveedor.id != proveedor_id
            ).first()
            if duplicado:
                return False, f"Ya existe otro proveedor con el NIT {nit.strip()}."

        prov_db.proveedor = proveedor.strip()
        prov_db.nombre_proveedor = nombre_proveedor.strip()
        prov_db.telefono = telefono.strip() if telefono.strip() else None
        prov_db.nit = nit.strip() if nit.strip() else None

        ids_seleccionados = set(ids_productos or [])

        productos_actuales = sesion.query(Producto).filter(Producto.proveedor_id == proveedor_id).all()
        for prod in productos_actuales:
            if prod.id not in ids_seleccionados:
                prod.proveedor_id = None

        # Vincular los productos seleccionados
        if ids_seleccionados:
            productos_nuevos = sesion.query(Producto).filter(Producto.id.in_(list(ids_seleccionados))).all()
            for prod in productos_nuevos:
                prod.proveedor_id = proveedor_id

        sesion.commit()
        return True, "Proveedor actualizado correctamente."
    except Exception as e:
        sesion.rollback()
        return False, f"Error al actualizar proveedor: {str(e)}"
    finally:
        sesion.close()


def eliminar_proveedor(proveedor_id):
    """Elimina limpiamente un proveedor desvinculando primero todos sus productos asociados."""
    sesion = SessionLocal()
    try:
        prov_db = sesion.query(Proveedor).filter(Proveedor.id == proveedor_id).first()
        if not prov_db:
            return False, "Proveedor no encontrado."

        nombre = prov_db.proveedor

        productos_vinculados = sesion.query(Producto).filter(Producto.proveedor_id == proveedor_id).all()
        for prod in productos_vinculados:
            prod.proveedor_id = None

        sesion.delete(prov_db)
        sesion.commit()
        return True, f"Proveedor '{nombre}' eliminado correctamente."
    except Exception as e:
        sesion.rollback()
        return False, f"Error al eliminar proveedor: {str(e)}"
    finally:
        sesion.close()