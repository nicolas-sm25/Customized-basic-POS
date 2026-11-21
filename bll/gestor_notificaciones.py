from datetime import datetime, timedelta
from dal.conexion_DB import SessionLocal
from dal.modelos.notificaciones import Notificacion
from dal.modelos.productos import Producto
from dal.modelos.contabilidad_caja import ContabilidadCaja
from dal.modelos.ventas import Venta

TIPOS_REINICIABLES_AL_INICIAR = {"CAJA_INCOMPLETA", "STOCK_NEGATIVO", "VENTA_ANTIGUA", "BASE_INACTIVA"}

ETIQUETAS_TIPO = {
    "CAJA_INCOMPLETA": "Caja Incompleta",
    "STOCK_NEGATIVO": "Stock Negativo",
    "STOCK_AGOTADO": "Stock Agotado",
    "COSTO_CERO": "Costo en $0",
    "VENTA_ANTIGUA": "Venta Guardada Antigua",
    "BASE_INACTIVA": "Paquete con Base Inactiva"
}


def registrar_notificacion_entidad(clave_unica, tipo, prioridad, descripcion, entidad_id=None, referencia_extra=None, reiniciar_ignoradas=False):
    """
    Crea o actualiza una única notificación por clave_unica.
    Elimina cualquier duplicado histórico con la misma clave_unica.
    """
    sesion = SessionLocal()
    try:
        existentes = sesion.query(Notificacion).filter(
            Notificacion.clave_unica == clave_unica
        ).order_by(Notificacion.id.desc()).all()

        ahora = datetime.now()

        if existentes:
            principal = existentes[0]
            for dup in existentes[1:]:
                sesion.delete(dup)

            principal.tipo = tipo
            principal.prioridad = prioridad
            principal.descripcion = descripcion
            principal.entidad_id = entidad_id
            principal.referencia_extra = referencia_extra

            if principal.estado == "Cumplida":
                principal.estado = "Activa"
                principal.fecha_creacion = ahora
                principal.ignorada_por = None
                principal.fecha_ignorada = None
            elif principal.estado == "Ignorada" and reiniciar_ignoradas:
                principal.estado = "Activa"
                principal.fecha_creacion = ahora
                principal.ignorada_por = None
                principal.fecha_ignorada = None
        else:
            nueva = Notificacion(
                clave_unica=clave_unica,
                tipo=tipo,
                prioridad=prioridad,
                descripcion=descripcion,
                entidad_id=entidad_id,
                referencia_extra=referencia_extra,
                estado="Activa",
                fecha_creacion=ahora
            )
            sesion.add(nueva)

        sesion.commit()
    except Exception as e:
        sesion.rollback()
        print(f"Error al registrar notificación ({clave_unica}): {e}")
    finally:
        sesion.close()


def registrar_notificacion_pool(tipo, prioridad, descripcion, entidad_id, referencia_extra=None):
    """Recicla ranuras cumplidas (TIPO_1, TIPO_2...) para eventos transaccionales sin duplicar activos/ignorados."""
    sesion = SessionLocal()
    try:
        ya_tracked = sesion.query(Notificacion).filter(
            Notificacion.tipo == tipo,
            Notificacion.entidad_id == entidad_id,
            Notificacion.estado.in_(["Activa", "Ignorada"])
        ).first()

        if ya_tracked:
            ya_tracked.descripcion = descripcion
            ya_tracked.prioridad = prioridad
            ya_tracked.referencia_extra = referencia_extra
            sesion.commit()
            return

        todas_del_tipo = sesion.query(Notificacion).filter(
            Notificacion.tipo == tipo
        ).order_by(Notificacion.id.asc()).all()

        ranura_libre = next((n for n in todas_del_tipo if n.estado == "Cumplida"), None)
        if ranura_libre:
            ranura_libre.entidad_id = entidad_id
            ranura_libre.descripcion = descripcion
            ranura_libre.prioridad = prioridad
            ranura_libre.referencia_extra = referencia_extra
            ranura_libre.estado = "Activa"
            ranura_libre.fecha_creacion = datetime.now()
            ranura_libre.ignorada_por = None
            ranura_libre.fecha_ignorada = None
        else:
            nuevo_indice = len(todas_del_tipo) + 1
            nueva = Notificacion(
                clave_unica=f"{tipo}_{nuevo_indice}",
                tipo=tipo,
                prioridad=prioridad,
                descripcion=descripcion,
                entidad_id=entidad_id,
                referencia_extra=referencia_extra,
                estado="Activa",
                fecha_creacion=datetime.now()
            )
            sesion.add(nueva)

        sesion.commit()
    except Exception as e:
        sesion.rollback()
        print(f"Error al registrar notificación pool ({tipo}): {e}")
    finally:
        sesion.close()


def cumplir_notificacion_por_clave(clave_unica):
    """Marca como Cumplida una notificación específica por su clave única."""
    sesion = SessionLocal()
    try:
        notif = sesion.query(Notificacion).filter(
            Notificacion.clave_unica == clave_unica,
            Notificacion.estado.in_(["Activa", "Ignorada"])
        ).first()
        if notif:
            notif.estado = "Cumplida"
            sesion.commit()
    except Exception as e:
        sesion.rollback()
        print(f"Error al cumplir notificación ({clave_unica}): {e}")
    finally:
        sesion.close()


def cumplir_notificacion_por_tipo_entidad(tipo, entidad_id):
    """Marca como Cumplida una notificación de pool según su tipo y entidad_id."""
    sesion = SessionLocal()
    try:
        notifs = sesion.query(Notificacion).filter(
            Notificacion.tipo == tipo,
            Notificacion.entidad_id == entidad_id,
            Notificacion.estado.in_(["Activa", "Ignorada"])
        ).all()
        for n in notifs:
            n.estado = "Cumplida"
        if notifs:
            sesion.commit()
    except Exception as e:
        sesion.rollback()
        print(f"Error al cumplir notificación ({tipo}, {entidad_id}): {e}")
    finally:
        sesion.close()


def evaluar_notificaciones_producto(producto_id, reiniciar_ignoradas=False):
    """Evalúa alertas de stock (individual o grupal), costo $0 y paquetes con base inactiva."""
    sesion = SessionLocal()
    try:
        prod = sesion.query(Producto).filter(Producto.id == producto_id).first()
        if not prod:
            return

        ids_a_evaluar = {prod.id}
        grupos_a_evaluar = set()

        if prod.grupo_stock_id:
            grupos_a_evaluar.add(prod.grupo_stock_id)

        if prod.es_paquete and prod.producto_base_id:
            ids_a_evaluar.add(prod.producto_base_id)
            base = sesion.query(Producto).filter(Producto.id == prod.producto_base_id).first()
            if base and base.grupo_stock_id:
                grupos_a_evaluar.add(base.grupo_stock_id)
        elif not prod.es_paquete:
            vinculados = sesion.query(Producto).filter(Producto.producto_base_id == prod.id).all()
            for v in vinculados:
                ids_a_evaluar.add(v.id)

        if grupos_a_evaluar:
            miembros_grupos = sesion.query(Producto).filter(Producto.grupo_stock_id.in_(list(grupos_a_evaluar))).all()
            for m in miembros_grupos:
                ids_a_evaluar.add(m.id)
                paqs = sesion.query(Producto).filter(Producto.producto_base_id == m.id).all()
                for pq in paqs:
                    ids_a_evaluar.add(pq.id)

        productos = sesion.query(Producto).filter(Producto.id.in_(list(ids_a_evaluar))).all()

        info_bases = {}
        for p in productos:
            if p.es_paquete and p.producto_base_id:
                base = sesion.query(Producto).filter(Producto.id == p.producto_base_id).first()
                if base:
                    info_bases[p.id] = {"id": base.id, "nombre": base.nombre, "activo": base.activo}

        datos_grupos = {}
        for gid in grupos_a_evaluar:
            activos_g = [m for m in productos if m.grupo_stock_id == gid and m.activo and not m.es_paquete]
            datos_grupos[gid] = {
                "miembros": [{"id": m.id, "nombre": m.nombre, "stock": m.stock} for m in activos_g]
            }
    finally:
        sesion.close()

    for p in productos:
        clave_neg = f"STOCK_NEGATIVO_PROD_{p.id}"
        clave_ago = f"STOCK_AGOTADO_PROD_{p.id}"
        clave_cos = f"COSTO_CERO_PROD_{p.id}"
        clave_base = f"BASE_INACTIVA_PROD_{p.id}"

        if not p.activo:
            cumplir_notificacion_por_clave(clave_neg)
            cumplir_notificacion_por_clave(clave_ago)
            cumplir_notificacion_por_clave(clave_cos)
            cumplir_notificacion_por_clave(clave_base)
            continue

        base_info = info_bases.get(p.id)
        if p.es_paquete and base_info and not base_info["activo"]:
            registrar_notificacion_entidad(
                clave_unica=clave_base,
                tipo="BASE_INACTIVA",
                prioridad="Alta",
                descripcion=f"El paquete '{p.nombre}' está activo, pero su producto base '{base_info['nombre']}' está desactivado.",
                entidad_id=p.id,
                referencia_extra=p.nombre,
                reiniciar_ignoradas=reiniciar_ignoradas
            )
        else:
            cumplir_notificacion_por_clave(clave_base)

        if p.es_paquete or p.grupo_stock_id:
            cumplir_notificacion_por_clave(clave_neg)
            cumplir_notificacion_por_clave(clave_ago)
        else:
            if p.stock < 0:
                cumplir_notificacion_por_clave(clave_ago)
                registrar_notificacion_entidad(
                    clave_unica=clave_neg,
                    tipo="STOCK_NEGATIVO",
                    prioridad="Alta",
                    descripcion=f"El producto '{p.nombre}' tiene stock negativo ({p.stock} uds). Verifica el inventario físico.",
                    entidad_id=p.id,
                    referencia_extra=p.nombre,
                    reiniciar_ignoradas=reiniciar_ignoradas
                )
            elif p.stock == 0:
                cumplir_notificacion_por_clave(clave_neg)
                registrar_notificacion_entidad(
                    clave_unica=clave_ago,
                    tipo="STOCK_AGOTADO",
                    prioridad="Media",
                    descripcion=f"El producto '{p.nombre}' se quedó sin unidades disponibles (0 uds).",
                    entidad_id=p.id,
                    referencia_extra=p.nombre,
                    reiniciar_ignoradas=reiniciar_ignoradas
                )
            else:
                cumplir_notificacion_por_clave(clave_neg)
                cumplir_notificacion_por_clave(clave_ago)

        if p.costo == 0:
            registrar_notificacion_entidad(
                clave_unica=clave_cos,
                tipo="COSTO_CERO",
                prioridad="Media",
                descripcion=f"El producto '{p.nombre}' está registrado con costo $0.",
                entidad_id=p.id,
                referencia_extra=p.nombre,
                reiniciar_ignoradas=reiniciar_ignoradas
            )
        else:
            cumplir_notificacion_por_clave(clave_cos)

    for gid, info in datos_grupos.items():
        clave_g_neg = f"STOCK_NEGATIVO_GRUPO_{gid}"
        clave_g_ago = f"STOCK_AGOTADO_GRUPO_{gid}"
        miembros = info["miembros"]

        if not miembros:
            cumplir_notificacion_por_clave(clave_g_neg)
            cumplir_notificacion_por_clave(clave_g_ago)
            continue

        stock_g = miembros[0]["stock"]
        nombres = [m["nombre"] for m in miembros]
        resumen_nombres = ", ".join(nombres) if len(nombres) <= 3 else f"{nombres[0]}, {nombres[1]} y {len(nombres) - 2} más"
        rep = miembros[0]

        if stock_g < 0:
            cumplir_notificacion_por_clave(clave_g_ago)
            registrar_notificacion_entidad(
                clave_unica=clave_g_neg,
                tipo="STOCK_NEGATIVO",
                prioridad="Alta",
                descripcion=f"El stock compartido ({resumen_nombres}) tiene stock negativo ({stock_g} uds). Verifica el inventario físico.",
                entidad_id=rep["id"],
                referencia_extra=rep["nombre"],
                reiniciar_ignoradas=reiniciar_ignoradas
            )
        elif stock_g == 0:
            cumplir_notificacion_por_clave(clave_g_neg)
            registrar_notificacion_entidad(
                clave_unica=clave_g_ago,
                tipo="STOCK_AGOTADO",
                prioridad="Media",
                descripcion=f"El stock compartido ({resumen_nombres}) se quedó sin unidades disponibles (0 uds).",
                entidad_id=rep["id"],
                referencia_extra=rep["nombre"],
                reiniciar_ignoradas=reiniciar_ignoradas
            )
        else:
            cumplir_notificacion_por_clave(clave_g_neg)
            cumplir_notificacion_por_clave(clave_g_ago)

def sincronizar_notificaciones_sistema(reiniciar_ignoradas=False):
    """Sincroniza cajas incompletas, ventas guardadas de >= 1 día y reinicia alertas operativas ignoradas."""
    sesion = SessionLocal()
    try:
        if reiniciar_ignoradas:
            ignoradas_reiniciables = sesion.query(Notificacion).filter(
                Notificacion.estado == "Ignorada",
                Notificacion.tipo.in_(list(TIPOS_REINICIABLES_AL_INICIAR))
            ).all()
            for n in ignoradas_reiniciables:
                n.estado = "Activa"
                n.ignorada_por = None
                n.fecha_ignorada = None
            if ignoradas_reiniciables:
                sesion.commit()

        cajas_incompletas = sesion.query(ContabilidadCaja).filter(
            ContabilidadCaja.estado == "Incompleta"
        ).all()
        ids_cajas_incompletas = {c.id for c in cajas_incompletas}

        limite_tiempo = datetime.now() - timedelta(days=1)
        ventas_viejas = sesion.query(Venta).filter(
            Venta.pagado == False,
            Venta.metodo_pago == "Pendiente",
            Venta.fecha_hora <= limite_tiempo
        ).all()
        ids_ventas_viejas = {v.id for v in ventas_viejas}

        activas_pool = sesion.query(Notificacion).filter(
            Notificacion.tipo.in_(["CAJA_INCOMPLETA", "VENTA_ANTIGUA"]),
            Notificacion.estado.in_(["Activa", "Ignorada"])
        ).all()
        for n in activas_pool:
            if n.tipo == "CAJA_INCOMPLETA" and n.entidad_id not in ids_cajas_incompletas:
                n.estado = "Cumplida"
            elif n.tipo == "VENTA_ANTIGUA" and n.entidad_id not in ids_ventas_viejas:
                n.estado = "Cumplida"
        sesion.commit()

        datos_cajas = [{
            "id": c.id,
            "encargado": c.usuario.nombre if c.usuario else "Desconocido",
            "fecha": c.fecha_apertura.strftime("%d/%m/%Y %I:%M %p") if c.fecha_apertura else "N/A"
        } for c in cajas_incompletas]

        datos_ventas = [{
            "id": v.id,
            "ref": v.referencia or "Sin referencia",
            "fecha": v.fecha_hora.strftime("%d/%m/%Y %I:%M %p"),
            "total": v.total
        } for v in ventas_viejas]
    finally:
        sesion.close()

    for c in datos_cajas:
        registrar_notificacion_pool(
            tipo="CAJA_INCOMPLETA",
            prioridad="Alta",
            descripcion=f"La caja de {c['encargado']} (abierta el {c['fecha']}) quedó incompleta sin cierre.",
            entidad_id=c["id"],
            referencia_extra=c["encargado"]
        )

    for v in datos_ventas:
        registrar_notificacion_pool(
            tipo="VENTA_ANTIGUA",
            prioridad="Media",
            descripcion=f"La venta guardada '{v['ref']}' (${int(v['total']):,}".replace(",", ".") + f") lleva pendiente desde el {v['fecha']}.",
            entidad_id=v["id"],
            referencia_extra=v["ref"]
        )


def obtener_notificaciones(estado="Activa", filtro_tipo=None, filtro_prioridad=None):
    """Devuelve las notificaciones filtradas por estado, tipo y prioridad."""
    sesion = SessionLocal()
    try:
        query = sesion.query(Notificacion).filter(Notificacion.estado == estado)
        if filtro_tipo and filtro_tipo != "Todos":
            query = query.filter(Notificacion.tipo == filtro_tipo)
        if filtro_prioridad and filtro_prioridad != "Todas":
            query = query.filter(Notificacion.prioridad == filtro_prioridad)

        lista = query.order_by(Notificacion.fecha_creacion.desc()).all()
        orden_prioridad = {"Alta": 0, "Media": 1, "Baja": 2}
        lista.sort(key=lambda n: orden_prioridad.get(n.prioridad, 9))

        return [{
            "id": n.id,
            "clave_unica": n.clave_unica,
            "tipo": n.tipo,
            "etiqueta_tipo": ETIQUETAS_TIPO.get(n.tipo, n.tipo),
            "prioridad": n.prioridad,
            "descripcion": n.descripcion,
            "entidad_id": n.entidad_id,
            "referencia_extra": n.referencia_extra,
            "estado": n.estado,
            "fecha": n.fecha_creacion.strftime("%d/%m/%Y %I:%M %p") if n.fecha_creacion else "N/A",
            "ignorada_por": n.ignorada_por,
            "fecha_ignorada": n.fecha_ignorada.strftime("%d/%m/%Y %I:%M %p") if n.fecha_ignorada else None
        } for n in lista]
    finally:
        sesion.close()


def contar_notificaciones_activas():
    sesion = SessionLocal()
    try:
        return sesion.query(Notificacion).filter(Notificacion.estado == "Activa").count()
    finally:
        sesion.close()


def ignorar_notificacion(notif_id, usuario_nombre="Usuario"):
    sesion = SessionLocal()
    try:
        n = sesion.query(Notificacion).filter(Notificacion.id == notif_id).first()
        if n:
            n.estado = "Ignorada"
            n.ignorada_por = usuario_nombre
            n.fecha_ignorada = datetime.now()
            sesion.commit()
            return True
        return False
    except Exception:
        sesion.rollback()
        return False
    finally:
        sesion.close()


def reactivar_notificacion(notif_id):
    sesion = SessionLocal()
    try:
        n = sesion.query(Notificacion).filter(Notificacion.id == notif_id).first()
        if n:
            n.estado = "Activa"
            n.ignorada_por = None
            n.fecha_ignorada = None
            sesion.commit()
            return True
        return False
    except Exception:
        sesion.rollback()
        return False
    finally:
        sesion.close()

def limpiar_notificaciones_producto(producto_id):
    """Marca como cumplidas todas las notificaciones asociadas a un producto eliminado."""
    claves = [
        f"STOCK_NEGATIVO_PROD_{producto_id}",
        f"STOCK_AGOTADO_PROD_{producto_id}",
        f"COSTO_CERO_PROD_{producto_id}",
        f"BASE_INACTIVA_PROD_{producto_id}",
    ]
    for clave in claves:
        cumplir_notificacion_por_clave(clave)


def limpiar_notificaciones_grupo(grupo_id):
    """Marca como cumplidas las notificaciones de un grupo de stock disuelto."""
    cumplir_notificacion_por_clave(f"STOCK_NEGATIVO_GRUPO_{grupo_id}")
    cumplir_notificacion_por_clave(f"STOCK_AGOTADO_GRUPO_{grupo_id}")