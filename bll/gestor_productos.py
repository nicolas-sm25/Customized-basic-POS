from dal.conexion_DB import SessionLocal
from dal.modelos.productos import Producto
from dal.modelos.grupos_stock import GrupoStock
from bll.gestor_notificaciones import (
    evaluar_notificaciones_producto,
    limpiar_notificaciones_producto,
    limpiar_notificaciones_grupo
)


def ajustar_stock_producto(sesion, producto_id, delta_unidades):
    """
    Aplica una variación de stock (positiva o negativa) sincronizando:
    - Todos los miembros del mismo grupo_stock_id (1:1).
    - Todos los paquetes vinculados a cualquiera de esos miembros.
    Debe llamarse ANTES de sesion.commit().
    """
    if delta_unidades == 0:
        return

    producto_db = sesion.query(Producto).filter(Producto.id == producto_id).first()
    if not producto_db:
        return

    if producto_db.es_paquete and producto_db.producto_base_id:
        producto_base = sesion.query(Producto).filter(Producto.id == producto_db.producto_base_id).first()
        if not producto_base:
            return

        nuevo_stock_base = producto_base.stock + (delta_unidades * producto_db.cantidad_por_paquete)
        _aplicar_stock_unitario_y_derivados(sesion, producto_base, nuevo_stock_base)
    else:
        nuevo_stock = producto_db.stock + delta_unidades
        _aplicar_stock_unitario_y_derivados(sesion, producto_db, nuevo_stock)


def _aplicar_stock_unitario_y_derivados(sesion, producto_unitario, nuevo_stock):
    """Actualiza un producto unitario, sus hermanos de grupo (si tiene) y todos los paquetes asociados."""
    stock_paquete_base = max(0, nuevo_stock)

    if producto_unitario.grupo_stock_id:
        miembros = sesion.query(Producto).filter(
            Producto.grupo_stock_id == producto_unitario.grupo_stock_id
        ).all()
        ids_miembros = []
        for m in miembros:
            m.stock = nuevo_stock
            ids_miembros.append(m.id)

        paquetes = sesion.query(Producto).filter(Producto.producto_base_id.in_(ids_miembros)).all()
        for paq in paquetes:
            if paq.cantidad_por_paquete > 0:
                paq.stock = stock_paquete_base // paq.cantidad_por_paquete
    else:
        producto_unitario.stock = nuevo_stock
        paquetes = sesion.query(Producto).filter(Producto.producto_base_id == producto_unitario.id).all()
        for paq in paquetes:
            if paq.cantidad_por_paquete > 0:
                paq.stock = stock_paquete_base // paq.cantidad_por_paquete


def _vincular_y_sumar_grupo(sesion, productos_a_unir, stock_extra_nuevo=0):
    """
    Une una lista de objetos Producto bajo un mismo GrupoStock sumando los stocks
    de cada grupo/producto distinto una sola vez.
    """
    grupos_contados = set()
    grupos_ids_orden = []
    total_stock = stock_extra_nuevo

    for p in productos_a_unir:
        if p.grupo_stock_id:
            if p.grupo_stock_id not in grupos_contados:
                total_stock += p.stock
                grupos_contados.add(p.grupo_stock_id)
                grupos_ids_orden.append(p.grupo_stock_id)
        else:
            total_stock += p.stock

    todos_miembros_dict = {p.id: p for p in productos_a_unir}
    if grupos_ids_orden:
        existentes_grupo = sesion.query(Producto).filter(
            Producto.grupo_stock_id.in_(grupos_ids_orden)
        ).all()
        for eg in existentes_grupo:
            todos_miembros_dict[eg.id] = eg

    todos_miembros = list(todos_miembros_dict.values())

    if grupos_ids_orden:
        grupo_principal_id = grupos_ids_orden[0]
        grupos_sobrantes = grupos_ids_orden[1:]
    else:
        nuevo_grupo = GrupoStock(nombre=f"Compartido: {todos_miembros[0].nombre}")
        sesion.add(nuevo_grupo)
        sesion.flush()
        grupo_principal_id = nuevo_grupo.id
        grupos_sobrantes = []

    for m in todos_miembros:
        m.grupo_stock_id = grupo_principal_id
        m.stock = total_stock

    ids_todos = [m.id for m in todos_miembros]
    paquetes = sesion.query(Producto).filter(Producto.producto_base_id.in_(ids_todos)).all()
    for paq in paquetes:
        if paq.cantidad_por_paquete > 0:
            paq.stock = total_stock // paq.cantidad_por_paquete

    for gid_viejo in grupos_sobrantes:
        g_obj = sesion.query(GrupoStock).filter(GrupoStock.id == gid_viejo).first()
        if g_obj:
            sesion.delete(g_obj)

    return grupo_principal_id, grupos_sobrantes


def agregar_producto(nombre, costo, precio_venta, codigo_barras=None, stock=0, es_paquete=False, producto_base_id=None, cantidad_por_paquete=1, ids_compartir_stock=None):
    sesion = SessionLocal()
    try:
        nuevo_prod = Producto(
            nombre=nombre,
            costo=costo,
            precio_venta=precio_venta,
            codigo_barras=codigo_barras,
            stock=stock,
            es_paquete=es_paquete,
            producto_base_id=producto_base_id if es_paquete else None,
            cantidad_por_paquete=cantidad_por_paquete if es_paquete else 1
        )
        sesion.add(nuevo_prod)
        sesion.flush()

        grupos_eliminados = []

        if es_paquete and producto_base_id and stock > 0:
            ajustar_stock_producto(sesion, nuevo_prod.id, stock)
        elif not es_paquete and ids_compartir_stock:
            seleccionados = sesion.query(Producto).filter(
                Producto.id.in_(ids_compartir_stock),
                Producto.es_paquete == False
            ).all()
            if seleccionados:
                nuevo_prod.stock = 0
                _, grupos_eliminados = _vincular_y_sumar_grupo(
                    sesion, [nuevo_prod] + seleccionados, stock_extra_nuevo=stock
                )

        prod_id = nuevo_prod.id
        sesion.commit()

        for gid in grupos_eliminados:
            limpiar_notificaciones_grupo(gid)

        if es_paquete and producto_base_id:
            evaluar_notificaciones_producto(producto_base_id)
        evaluar_notificaciones_producto(prod_id)

        return True, f"Producto '{nombre}' agregado exitosamente."
    except Exception as e:
        sesion.rollback()
        return False, f"Error al guardar: {str(e)}"
    finally:
        sesion.close()


def buscar_productos_por_nombre(nombre_parcial):
    sesion = SessionLocal()
    try:
        criterio_limpio = nombre_parcial.replace(" ", "")
        criterio_like = "%" + "%".join(list(criterio_limpio)) + "%"

        productos = sesion.query(Producto).filter(
            Producto.nombre.ilike(criterio_like)
        ).all()

        return [{
            "id": p.id,
            "nombre": p.nombre,
            "codigo_barras": p.codigo_barras,
            "costo": p.costo,
            "precio_venta": p.precio_venta,
            "stock": p.stock,
            "activo": p.activo
        } for p in productos]
    except Exception:
        return []
    finally:
        sesion.close()


def buscar_producto_por_codigo(codigo):
    sesion = SessionLocal()
    try:
        producto = sesion.query(Producto).filter(Producto.codigo_barras == codigo).first()
        if producto:
            return {
                "id": producto.id,
                "nombre": producto.nombre,
                "codigo_barras": producto.codigo_barras,
                "costo": producto.costo,
                "precio_venta": producto.precio_venta,
                "stock": producto.stock,
                "activo": producto.activo
            }
        return None
    except Exception:
        return None
    finally:
        sesion.close()


def actualizar_producto(id_producto, nombre, costo, precio_venta, codigo_barras, stock_nuevo):
    sesion = SessionLocal()
    try:
        producto = sesion.query(Producto).filter(Producto.id == id_producto).first()
        if not producto:
            return False, "Producto no encontrado en la base de datos."

        diferencia_stock = stock_nuevo - producto.stock
        if diferencia_stock != 0:
            ajustar_stock_producto(sesion, id_producto, diferencia_stock)

        producto.nombre = nombre
        producto.costo = costo
        producto.precio_venta = precio_venta
        producto.codigo_barras = codigo_barras
        producto.stock = stock_nuevo

        sesion.commit()
        evaluar_notificaciones_producto(id_producto)

        return True, "Producto actualizado correctamente."
    except Exception as e:
        sesion.rollback()
        return False, f"Error interno al intentar actualizar el producto: {str(e)}"
    finally:
        sesion.close()


def sincronizar_stock_relacional(sesion, producto_id, cantidad_agregada):
    """Ajusta el inventario manteniendo compatibilidad con llamadas existentes."""
    ajustar_stock_producto(sesion, producto_id, cantidad_agregada)


def obtener_productos_unitarios():
    """Devuelve solo los productos que NO son paquetes y están ACTIVOS."""
    sesion = SessionLocal()
    try:
        productos = sesion.query(Producto).filter(
            Producto.es_paquete == False,
            Producto.activo == True
        ).order_by(Producto.nombre.asc()).all()
        return [{
            "id": p.id,
            "nombre": p.nombre,
            "stock": p.stock,
            "grupo_stock_id": p.grupo_stock_id
        } for p in productos]
    finally:
        sesion.close()


def obtener_inventario_completo():
    """Devuelve todos los productos (activos e inactivos) con información de paquetes y stock compartido."""
    sesion = SessionLocal()
    try:
        productos = sesion.query(Producto).all()
        conteo_grupos = {}
        for p in productos:
            if p.grupo_stock_id:
                conteo_grupos[p.grupo_stock_id] = conteo_grupos.get(p.grupo_stock_id, 0) + 1

        resultado = []
        for p in productos:
            nombre_base = "N/A"
            unidad_inactiva = False

            if p.es_paquete and p.producto_base_id:
                base = sesion.query(Producto).filter(Producto.id == p.producto_base_id).first()
                if base:
                    nombre_base = f"{base.nombre} (x{p.cantidad_por_paquete})"
                    if not base.activo:
                        unidad_inactiva = True
                else:
                    nombre_base = f"ID: {p.producto_base_id} (x{p.cantidad_por_paquete})"
            elif p.es_paquete:
                nombre_base = f"Paquete (x{p.cantidad_por_paquete})"

            es_compartido = bool(p.grupo_stock_id and conteo_grupos.get(p.grupo_stock_id, 0) > 1)
            cant_compartidos = conteo_grupos.get(p.grupo_stock_id, 0) if es_compartido else 0

            resultado.append({
                "id": p.id,
                "nombre": p.nombre,
                "costo": p.costo,
                "precio_venta": p.precio_venta,
                "stock": p.stock,
                "es_paquete": p.es_paquete,
                "activo": p.activo,
                "info_paquete": nombre_base,
                "unidad_inactiva": unidad_inactiva,
                "es_compartido": es_compartido,
                "cant_compartidos": cant_compartidos
            })
        return resultado
    finally:
        sesion.close()


def desactivar_producto_db(producto_id):
    """Desactiva lógicamente el producto y aplica desactivación en cascada si es unidad base."""
    sesion = SessionLocal()
    try:
        producto = sesion.query(Producto).filter(Producto.id == producto_id).first()
        if not producto:
            return False, "Producto no encontrado."

        producto.activo = False

        if not producto.es_paquete:
            paquetes_vinculados = sesion.query(Producto).filter(Producto.producto_base_id == producto.id).all()
            for paquete in paquetes_vinculados:
                paquete.activo = False

        nombre_prod = producto.nombre
        sesion.commit()
        evaluar_notificaciones_producto(producto_id)
        return True, f"Producto '{nombre_prod}' desactivado correctamente."
    except Exception as e:
        sesion.rollback()
        return False, f"Error al desactivar: {str(e)}"
    finally:
        sesion.close()


def reactivar_producto_db(producto_id):
    """Reactiva lógicamente el producto y aplica activación en cascada si es unidad base."""
    sesion = SessionLocal()
    try:
        producto = sesion.query(Producto).filter(Producto.id == producto_id).first()
        if not producto:
            return False, "Producto no encontrado."

        producto.activo = True

        if not producto.es_paquete:
            paquetes_vinculados = sesion.query(Producto).filter(Producto.producto_base_id == producto.id).all()
            for paquete in paquetes_vinculados:
                paquete.activo = True

        nombre_prod = producto.nombre
        sesion.commit()
        evaluar_notificaciones_producto(producto_id)
        return True, f"Producto '{nombre_prod}' reactivado correctamente."
    except Exception as e:
        sesion.rollback()
        return False, f"Error al reactivar: {str(e)}"
    finally:
        sesion.close()


def obtener_producto_por_id(producto_id):
    """Obtiene el diccionario completo de un producto por su ID, incluyendo hermanos de grupo."""
    sesion = SessionLocal()
    try:
        p = sesion.query(Producto).filter(Producto.id == producto_id).first()
        if not p:
            return None

        hermanos = []
        if p.grupo_stock_id:
            miembros = sesion.query(Producto).filter(
                Producto.grupo_stock_id == p.grupo_stock_id,
                Producto.id != p.id
            ).all()
            hermanos = [{"id": m.id, "nombre": m.nombre} for m in miembros]

        return {
            "id": p.id,
            "nombre": p.nombre,
            "codigo_barras": p.codigo_barras,
            "costo": p.costo,
            "precio_venta": p.precio_venta,
            "stock": p.stock,
            "activo": p.activo,
            "es_paquete": p.es_paquete,
            "producto_base_id": p.producto_base_id,
            "cantidad_por_paquete": p.cantidad_por_paquete,
            "grupo_stock_id": p.grupo_stock_id,
            "hermanos_stock": hermanos
        }
    finally:
        sesion.close()


def verificar_ventas_producto(producto_id):
    """Retorna True si el producto ya se vendió alguna vez o está en un pedido guardado."""
    from dal.modelos.ventas import DetalleVenta
    sesion = SessionLocal()
    try:
        tiene_ventas = sesion.query(DetalleVenta).filter(DetalleVenta.producto_id == producto_id).first()
        return tiene_ventas is not None
    finally:
        sesion.close()


def eliminar_producto_definitivo(producto_id):
    """Borra el producto de la base de datos y disuelve su grupo de stock si queda con 1 solo miembro."""
    sesion = SessionLocal()
    try:
        producto = sesion.query(Producto).filter(Producto.id == producto_id).first()
        if not producto:
            return False, "Producto no encontrado."

        grupo_id = producto.grupo_stock_id
        sesion.delete(producto)
        sesion.flush()

        grupo_disuelto_id = None
        sobreviviente_id = None

        if grupo_id:
            restantes = sesion.query(Producto).filter(Producto.grupo_stock_id == grupo_id).all()
            if len(restantes) <= 1:
                if len(restantes) == 1:
                    restantes[0].grupo_stock_id = None
                    sobreviviente_id = restantes[0].id
                g_obj = sesion.query(GrupoStock).filter(GrupoStock.id == grupo_id).first()
                if g_obj:
                    sesion.delete(g_obj)
                grupo_disuelto_id = grupo_id
            elif restantes:
                sobreviviente_id = restantes[0].id

        sesion.commit()
        limpiar_notificaciones_producto(producto_id)
        if grupo_disuelto_id:
            limpiar_notificaciones_grupo(grupo_disuelto_id)
        if sobreviviente_id:
            evaluar_notificaciones_producto(sobreviviente_id)

        return True, "Producto eliminado definitivamente."
    except Exception as e:
        sesion.rollback()
        return False, f"Error al eliminar: {e}"
    finally:
        sesion.close()


def actualizar_producto_avanzado(producto_id, nombre, codigo, es_paquete, producto_base_id, cantidad_paquete, compartir_stock=False, ids_compartir_stock=None):
    """Actualiza datos sensibles, relación de paquete o grupo de stock compartido (sumando stocks)."""
    sesion = SessionLocal()
    try:
        producto = sesion.query(Producto).filter(Producto.id == producto_id).first()
        if not producto:
            return False, "Producto no encontrado."

        producto.nombre = nombre
        producto.codigo_barras = codigo if codigo else None

        old_grupo_id = producto.grupo_stock_id
        grupos_a_limpiar = []
        ids_a_reevaluar = {producto_id}

        if es_paquete:
            compartir_stock = False
            ids_compartir_stock = []

        producto.es_paquete = es_paquete
        producto.producto_base_id = producto_base_id if es_paquete else None
        producto.cantidad_por_paquete = cantidad_paquete if es_paquete else 1

        ids_elegidos = set(ids_compartir_stock or [])
        ids_elegidos.discard(producto_id)

        if old_grupo_id:
            miembros_viejos = sesion.query(Producto).filter(Producto.grupo_stock_id == old_grupo_id).all()
            if not compartir_stock or not ids_elegidos:
                producto.grupo_stock_id = None
                restantes = [m for m in miembros_viejos if m.id != producto_id]
                for r in restantes:
                    ids_a_reevaluar.add(r.id)
                if len(restantes) <= 1:
                    if len(restantes) == 1:
                        restantes[0].grupo_stock_id = None
                    g_obj = sesion.query(GrupoStock).filter(GrupoStock.id == old_grupo_id).first()
                    if g_obj:
                        sesion.delete(g_obj)
                    grupos_a_limpiar.append(old_grupo_id)
            else:
                for m in miembros_viejos:
                    if m.id != producto_id and m.id not in ids_elegidos:
                        m.grupo_stock_id = None
                        ids_a_reevaluar.add(m.id)

        if compartir_stock and ids_elegidos:
            seleccionados = sesion.query(Producto).filter(
                Producto.id.in_(list(ids_elegidos)),
                Producto.es_paquete == False
            ).all()
            if seleccionados:
                _, sobrantes = _vincular_y_sumar_grupo(sesion, [producto] + seleccionados, stock_extra_nuevo=0)
                grupos_a_limpiar.extend(sobrantes)
                for s in seleccionados:
                    ids_a_reevaluar.add(s.id)

        sesion.commit()

        for gid in set(grupos_a_limpiar):
            limpiar_notificaciones_grupo(gid)
        for pid in ids_a_reevaluar:
            evaluar_notificaciones_producto(pid)

        return True, "Edición avanzada guardada correctamente."
    except Exception as e:
        sesion.rollback()
        return False, f"Error en BD: {e}"
    finally:
        sesion.close()


def sumar_stock_rapido(producto_id, cantidad_agregada):
    """Suma unidades al stock sincronizando grupos compartidos y paquetes."""
    if cantidad_agregada <= 0:
        return False, "La cantidad a añadir debe ser mayor a 0."

    sesion = SessionLocal()
    try:
        producto = sesion.query(Producto).filter(Producto.id == producto_id).first()
        if not producto:
            return False, "Producto no encontrado."

        ajustar_stock_producto(sesion, producto_id, cantidad_agregada)
        sesion.commit()
        evaluar_notificaciones_producto(producto_id)
        return True, "Stock actualizado correctamente."
    except Exception as e:
        sesion.rollback()
        return False, f"Error al sumar stock: {e}"
    finally:
        sesion.close()

def actualizar_costo_rapido(producto_id, nuevo_costo):
    """Actualiza únicamente el costo de un producto y evalúa sus notificaciones."""
    if nuevo_costo <= 0:
        return False, "El costo debe ser mayor a $0."

    sesion = SessionLocal()
    try:
        producto = sesion.query(Producto).filter(Producto.id == producto_id).first()
        if not producto:
            return False, "Producto no encontrado."

        producto.costo = nuevo_costo
        sesion.commit()
        evaluar_notificaciones_producto(producto_id)
        return True, "Costo actualizado correctamente."
    except Exception as e:
        sesion.rollback()
        return False, f"Error al actualizar costo: {e}"
    finally:
        sesion.close()