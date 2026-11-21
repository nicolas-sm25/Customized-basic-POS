from datetime import datetime
from dal.conexion_DB import SessionLocal
from dal.modelos.contabilidad_caja import ContabilidadCaja
from dal.modelos.contabilidad_caja import GastoCaja
from dal.modelos.ventas import Venta
from bll.gestor_notificaciones import evaluar_notificaciones_producto, cumplir_notificacion_por_tipo_entidad
from bll.gestor_productos import ajustar_stock_producto


# --- VERIFICAR SI HAY UNA CAJA ABIERTA ---
def obtener_caja_abierta():
    sesion = SessionLocal()
    try:
        return sesion.query(ContabilidadCaja).filter(ContabilidadCaja.estado == "Abierta").first()
    except Exception as e:
        print(f"Error crítico al consultar caja: {e}")
        return None
    finally:
        sesion.close()


# --- MARCAR CAJAS HUÉRFANAS COMO INCOMPLETAS ---
def verificar_cierre_inesperado():
    """Se ejecuta una sola vez al iniciar la aplicación. Pasa cualquier caja 'Abierta' a 'Incompleta'."""
    sesion = SessionLocal()
    try:
        cajas_huerfanas = sesion.query(ContabilidadCaja).filter(ContabilidadCaja.estado == "Abierta").all()
        if not cajas_huerfanas:
            return 0
        for caja in cajas_huerfanas:
            caja.estado = "Incompleta"
        sesion.commit()
        return len(cajas_huerfanas)
    except Exception as e:
        sesion.rollback()
        print(f"Error al verificar cierre inesperado: {e}")
        return 0
    finally:
        sesion.close()


def obtener_caja_incompleta():
    """Retorna los datos de la caja incompleta más reciente para mostrar el aviso en apertura."""
    sesion = SessionLocal()
    try:
        caja = sesion.query(ContabilidadCaja).filter(
            ContabilidadCaja.estado == "Incompleta"
        ).order_by(ContabilidadCaja.id.desc()).first()

        if not caja:
            return None

        return {
            "id": caja.id,
            "encargado": caja.usuario.nombre if caja.usuario else "Desconocido",
            "fecha_apertura": caja.fecha_apertura.strftime("%d/%m/%Y %I:%M %p") if caja.fecha_apertura else "N/A",
            "base": caja.base_efectivo,
            "ventas": caja.ventas_efectivo + caja.ventas_nequi,
            "gastos": caja.gastos_totales
        }
    finally:
        sesion.close()


def recuperar_caja_incompleta(caja_id, nombre_usuario):
    """Reactiva una caja incompleta dejando constancia de quién y cuándo la recuperó."""
    sesion = SessionLocal()
    try:
        if sesion.query(ContabilidadCaja).filter(ContabilidadCaja.estado == "Abierta").first():
            return False, "Ya existe una caja abierta en este momento."

        caja = sesion.query(ContabilidadCaja).filter(
            ContabilidadCaja.id == caja_id,
            ContabilidadCaja.estado == "Incompleta"
        ).first()

        if not caja:
            return False, "No se encontró la caja incompleta."

        caja.estado = "Abierta"
        caja.recuperada_por = nombre_usuario
        caja.fecha_recuperacion = datetime.now()
        sesion.commit()
        cumplir_notificacion_por_tipo_entidad("CAJA_INCOMPLETA", caja_id)
        return True, "Caja recuperada exitosamente."
    except Exception as e:
        sesion.rollback()
        return False, f"Error al recuperar caja: {e}"
    finally:
        sesion.close()


# --- INICIAR CAJA ---
def abrir_caja(base_efectivo, usuario_id=None):
    """Crea un nuevo registro de caja y lo marca como abierto."""
    sesion = SessionLocal()
    try:
        if obtener_caja_abierta():
            return False, "Ya existe una caja abierta. Debe cerrarla primero."

        nueva_caja = ContabilidadCaja(
            base_efectivo=base_efectivo,
            usuario_id=usuario_id,
            estado="Abierta"
        )
        sesion.add(nueva_caja)
        sesion.commit()
        return True, "Caja abierta exitosamente."
    except Exception as e:
        sesion.rollback()
        return False, f"Error en la base de datos al abrir caja: {str(e)}"
    finally:
        sesion.close()


# --- CERRAR CAJA ---
def cerrar_caja():
    sesion = SessionLocal()
    try:
        cajas_abiertas = sesion.query(ContabilidadCaja).filter(ContabilidadCaja.estado == "Abierta").all()
        if not cajas_abiertas:
            return False, "No hay ninguna caja abierta en este momento."

        ids_cerradas = [c.id for c in cajas_abiertas]
        for caja in cajas_abiertas:
            caja.estado = "Cerrada"
            caja.fecha_cierre = datetime.now()

        sesion.commit()
        for cid in ids_cerradas:
            cumplir_notificacion_por_tipo_entidad("CAJA_INCOMPLETA", cid)
        return True, "Caja cerrada exitosamente."
    except Exception as e:
        sesion.rollback()
        return False, f"Error al cerrar la caja: {str(e)}"
    finally:
        sesion.close()

def registrar_gasto(caja_id, descripcion, monto, tipo_gasto="Dinero", producto_id=None, cantidad_descontada=0):
    """Registra una salida de dinero o una baja de inventario (merma) descontando stock."""
    from dal.modelos.productos import Producto
    sesion = SessionLocal()
    try:
        nuevo_gasto = GastoCaja(
            caja_id=caja_id,
            descripcion=descripcion,
            monto=monto,
            tipo_gasto=tipo_gasto,
            producto_id=producto_id if tipo_gasto == "Inventario" else None,
            cantidad_descontada=cantidad_descontada if tipo_gasto == "Inventario" else None
        )
        sesion.add(nuevo_gasto)

        if tipo_gasto == "Inventario" and producto_id:
            producto = sesion.query(Producto).filter(Producto.id == producto_id).first()
            if not producto:
                sesion.rollback()
                return False, "El producto seleccionado no existe."
            ajustar_stock_producto(sesion, producto_id, -cantidad_descontada)

        caja = sesion.query(ContabilidadCaja).filter(ContabilidadCaja.id == caja_id).first()
        if caja:
            if tipo_gasto == "Dinero":
                caja.gastos_totales += monto

        sesion.commit()
        if tipo_gasto == "Dinero":
            from bll.gestor_impresora import abrir_cajon_monedero
            abrir_cajon_monedero()
        elif tipo_gasto == "Inventario" and producto_id:
            evaluar_notificaciones_producto(producto_id)

        msg = "Gasto registrado correctamente." if tipo_gasto == "Dinero" else "Baja de inventario registrada."
        return True, msg
    except Exception as e:
        sesion.rollback()
        return False, f"Error al registrar gasto: {e}"
    finally:
        sesion.close()
        
def registrar_mermas_lote(caja_id, descripcion, items_merma):
    """Registra múltiples bajas de inventario (mermas) en una sola transacción."""
    from dal.modelos.productos import Producto
    sesion = SessionLocal()
    try:
        ids_afectados = set()
        for item in items_merma:
            prod_id = item["id"]
            cant = item["cantidad"]
            costo_perdido = item["subtotal"]
            ids_afectados.add(prod_id)

            nuevo_gasto = GastoCaja(
                caja_id=caja_id,
                descripcion=descripcion,
                tipo_gasto="Inventario",
                monto=costo_perdido,
                producto_id=prod_id,
                cantidad_descontada=cant
            )
            sesion.add(nuevo_gasto)

            producto = sesion.query(Producto).filter(Producto.id == prod_id).first()
            if not producto:
                sesion.rollback()
                return False, f"El producto '{item['nombre']}' no existe."
            ajustar_stock_producto(sesion, prod_id, -cant)

        sesion.commit()
        for pid in ids_afectados:
            evaluar_notificaciones_producto(pid)

        return True, "Baja de inventario registrada correctamente."
    except Exception as e:
        sesion.rollback()
        return False, f"Error al registrar baja de inventario: {e}"
    finally:
        sesion.close()

def obtener_resumen_caja(caja_id):
    """Devuelve los totales calculados de cualquier caja (Abierta, Cerrada o Incompleta)."""
    sesion = SessionLocal()
    try:
        caja = sesion.query(ContabilidadCaja).filter(ContabilidadCaja.id == caja_id).first()
        if not caja:
            return None

        total_ventas = caja.ventas_efectivo + caja.ventas_nequi
        ventas_pagadas = sesion.query(Venta).filter(Venta.caja_id == caja_id, Venta.pagado == True).all()

        ganancia_efectivo = sum(v.ganancia_total for v in ventas_pagadas if v.metodo_pago == "Efectivo")
        ganancia_nequi = sum(v.ganancia_total for v in ventas_pagadas if v.metodo_pago == "Nequi")
        ganancia_bruta = ganancia_efectivo + ganancia_nequi
        costos_totales = total_ventas - ganancia_bruta

        return {
            "base": caja.base_efectivo,
            "efectivo": caja.ventas_efectivo,
            "nequi": caja.ventas_nequi,
            "gastos": caja.gastos_totales,
            "total_ventas": total_ventas,
            "costos": costos_totales,
            "ganancia_efectivo": ganancia_efectivo,
            "ganancia_nequi": ganancia_nequi,
            "ganancia_bruta": ganancia_bruta,
            "ganancia_neta": ganancia_bruta - caja.gastos_totales,
            "efectivo_esperado": caja.base_efectivo + caja.ventas_efectivo - caja.gastos_totales,
            "efectivo_cierre": caja.total_efectivo_cierre,
            "diferencia": caja.diferencia if caja.diferencia is not None else 0,
            "estado": caja.estado,
            "abierta": (caja.estado == "Abierta"),
            "recuperada_por": caja.recuperada_por,
            "fecha_recuperacion": caja.fecha_recuperacion.strftime("%d/%m/%Y %I:%M %p") if caja.fecha_recuperacion else None
        }
    finally:
        sesion.close()

def cerrar_caja_definitiva(caja_id, efectivo_fisico, diferencia, auditada_por=None):
    """Guarda los resultados físicos y marca la caja como Cerrada (sirve para cierre normal o auditoría)."""
    sesion = SessionLocal()
    try:
        caja = sesion.query(ContabilidadCaja).filter(ContabilidadCaja.id == caja_id).first()
        if caja:
            estado_anterior = caja.estado
            caja.estado = "Cerrada"
            caja.fecha_cierre = datetime.now()
            caja.total_efectivo_cierre = efectivo_fisico
            caja.diferencia = diferencia

            if estado_anterior == "Incompleta" and auditada_por and not caja.recuperada_por:
                caja.recuperada_por = f"Recuperada por {auditada_por}"
                caja.fecha_recuperacion = datetime.now()

            resumen = obtener_resumen_caja(caja_id)
            if resumen:
                caja.costos_totales = resumen['costos']
                caja.ganancia_total = resumen['ganancia_bruta']

            sesion.commit()
            cumplir_notificacion_por_tipo_entidad("CAJA_INCOMPLETA", caja_id)
            return True, "Caja cerrada correctamente."
        return False, "Caja no encontrada."
    except Exception as e:
        sesion.rollback()
        return False, str(e)
    finally:
        sesion.close()

def obtener_historial_cajas():
    sesion = SessionLocal()
    try:
        cajas = sesion.query(ContabilidadCaja).order_by(ContabilidadCaja.id.desc()).all()
        resultado = []
        for c in cajas:
            ganancia_bruta = c.ganancia_total if c.ganancia_total else 0
            nombre_encargado = c.usuario.nombre if c.usuario else "Desconocido"

            if c.estado == "Cerrada" and c.fecha_cierre:
                fecha_cierre_str = c.fecha_cierre.strftime("%d/%m/%Y %I:%M %p")
            elif c.estado == "Incompleta":
                fecha_cierre_str = "Incompleta"
            else:
                fecha_cierre_str = "En curso..."

            fecha_rec_str = c.fecha_recuperacion.strftime("%d/%m/%Y %I:%M %p") if c.fecha_recuperacion else None

            resultado.append({
                "id": c.id,
                "encargado": nombre_encargado,
                "fecha_apertura": c.fecha_apertura.strftime("%d/%m/%Y %I:%M %p") if c.fecha_apertura else "N/A",
                "fecha_cierre": fecha_cierre_str,
                "base": c.base_efectivo,
                "ventas": c.ventas_efectivo + c.ventas_nequi,
                "gastos": c.gastos_totales,
                "ganancia_neta": ganancia_bruta - c.gastos_totales,
                "diferencia": c.diferencia if c.diferencia is not None else 0,
                "estado": c.estado,
                "recuperada_por": c.recuperada_por,
                "fecha_recuperacion": fecha_rec_str
            })
        return resultado
    finally:
        sesion.close()

def obtener_detalles_turno(caja_id):
    """Retorna (ventas_pagadas, ventas_guardadas, gastos) de una caja específica."""
    from dal.modelos.ventas import Venta
    sesion = SessionLocal()
    try:
        ventas_db = sesion.query(Venta).filter(
            Venta.caja_id == caja_id,
            Venta.pagado == True
        ).order_by(Venta.fecha_hora.desc()).all()

        guardadas_db = sesion.query(Venta).filter(
            Venta.caja_id == caja_id,
            Venta.pagado == False
        ).order_by(Venta.fecha_hora.desc()).all()

        gastos_db = sesion.query(GastoCaja).filter(
            GastoCaja.caja_id == caja_id
        ).order_by(GastoCaja.fecha_hora.desc()).all()

        ventas = []
        for v in ventas_db:
            detalles_lista = [{
                "producto": d.producto.nombre if d.producto else f"Producto #{d.producto_id}",
                "cantidad": d.cantidad,
                "precio_unitario": d.precio_unitario,
                "subtotal": d.subtotal
            } for d in v.detalles]

            es_guardada_anterior = False
            fecha_guardada = None
            referencia_guardada = None

            if v.referencia and v.referencia.startswith("GUARDADA|"):
                partes = v.referencia.split("|", 3)
                if len(partes) == 4:
                    es_guardada_anterior = True
                    fecha_guardada = partes[2]
                    referencia_guardada = partes[3]

            ventas.append({
                "id": v.id,
                "hora": v.fecha_hora.strftime("%I:%M %p"),
                "metodo_pago": v.metodo_pago or "Efectivo",
                "cantidad_articulos": sum(d.cantidad for d in v.detalles),
                "total": v.total,
                "ganancia": v.ganancia_total,
                "es_guardada_anterior": es_guardada_anterior,
                "fecha_guardada": fecha_guardada,
                "referencia_guardada": referencia_guardada,
                "detalles": detalles_lista
            })

        ventas_guardadas = []
        for vg in guardadas_db:
            detalles_lista = [{
                "producto": d.producto.nombre if d.producto else f"Producto #{d.producto_id}",
                "cantidad": d.cantidad,
                "precio_unitario": d.precio_unitario,
                "subtotal": d.subtotal
            } for d in vg.detalles]

            items_recuperar = [{
                "id": d.producto_id,
                "nombre": d.producto.nombre if d.producto else f"Producto #{d.producto_id}",
                "precio_venta": d.precio_unitario,
                "costo": d.producto.costo if d.producto else 0,
                "cantidad": d.cantidad,
                "subtotal": d.subtotal
            } for d in vg.detalles]

            metodo = vg.metodo_pago or "Pendiente"
            if metodo.startswith("Eliminada"):
                estado_guardada = "Eliminada"
                if "|" in metodo:
                    fecha_elim = metodo.split("|", 1)[1]
                    texto_pago = f"Eliminada el {fecha_elim}"
                else:
                    texto_pago = "Eliminada"
            elif metodo.startswith("Pagada|"):
                estado_guardada = "Pagado"
                fecha_pago = metodo.split("|", 1)[1]
                texto_pago = f"Pagada el {fecha_pago}"
            else:
                estado_guardada = "Pendiente"
                texto_pago = ""

            ventas_guardadas.append({
                "id": vg.id,
                "hora": vg.fecha_hora.strftime("%I:%M %p"),
                "fecha": vg.fecha_hora.strftime("%d/%m/%Y %I:%M %p") if vg.fecha_hora else "",
                "fecha_solo": vg.fecha_hora.strftime("%d-%m-%Y") if vg.fecha_hora else "",
                "cliente": vg.referencia or "Sin Nombre",
                "referencia": vg.referencia or "Sin referencia",
                "estado": estado_guardada,
                "texto_pago": texto_pago,
                "cantidad_articulos": sum(d.cantidad for d in vg.detalles),
                "total": vg.total,
                "detalles": detalles_lista,
                "items": items_recuperar
            })

        gastos = [{
            "id": g.id,
            "hora": g.fecha_hora.strftime("%I:%M %p"),
            "tipo": g.tipo_gasto or "Dinero",
            "descripcion": g.descripcion,
            "monto": g.monto,
            "producto": g.producto.nombre if g.producto else None,
            "cantidad": g.cantidad_descontada
        } for g in gastos_db]

        return ventas, ventas_guardadas, gastos
    finally:
        sesion.close()

def obtener_todos_los_gastos():
    """Retorna el historial global de todos los gastos y mermas registrados."""
    sesion = SessionLocal()
    try:
        gastos_db = sesion.query(GastoCaja).order_by(GastoCaja.fecha_hora.desc()).all()
        resultado = []
        for g in gastos_db:
            encargado = g.caja.usuario.nombre if (g.caja and g.caja.usuario) else "Desconocido"
            resultado.append({
                "id": g.id,
                "fecha_hora": g.fecha_hora.strftime("%d-%m-%Y %I:%M %p"),
                "encargado": encargado,
                "tipo": g.tipo_gasto or "Dinero",
                "descripcion": g.descripcion,
                "producto": g.producto.nombre if g.producto else "-",
                "cantidad": g.cantidad_descontada if g.cantidad_descontada else "-",
                "monto": g.monto
            })
        return resultado
    finally:
        sesion.close()

def obtener_caja_por_venta(venta_id):
    """Retorna el diccionario del turno (caja) donde se registró una venta específica."""
    from dal.modelos.ventas import Venta
    sesion = SessionLocal()
    try:
        venta = sesion.query(Venta).filter(Venta.id == venta_id).first()
        if not venta or not venta.caja:
            return None

        c = venta.caja
        return {
            "id": c.id,
            "encargado": c.usuario.nombre if c.usuario else "Desconocido",
            "fecha_apertura": c.fecha_apertura.strftime("%d/%m/%Y %I:%M %p") if c.fecha_apertura else "N/A",
            "estado": c.estado
        }
    finally:
        sesion.close()