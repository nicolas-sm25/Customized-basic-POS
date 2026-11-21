from dal.conexion_DB import SessionLocal
from dal.modelos.ventas import Venta, DetalleVenta
from dal.modelos.productos import Producto
from dal.modelos.contabilidad_caja import ContabilidadCaja
from bll.gestor_notificaciones import evaluar_notificaciones_producto, cumplir_notificacion_por_tipo_entidad
from bll.gestor_productos import ajustar_stock_producto
from datetime import datetime


def registrar_venta(carrito, metodo_pago, caja_id, nombre_cliente=None, pagado=True, venta_guardada_origen=None):
    """
    Guarda la venta, sus detalles, descuenta inventario y actualiza el saldo de la caja.
    Si proviene de una venta guardada anterior, marca la original como pagada con fecha sin borrarla.
    """
    sesion = SessionLocal()

    try:
        total_venta = 0.0
        ganancia_venta = 0.0

        referencia_final = nombre_cliente
        if pagado and venta_guardada_origen:
            referencia_final = (
                f"GUARDADA|{venta_guardada_origen['id']}|"
                f"{venta_guardada_origen['fecha_solo']}|{venta_guardada_origen['cliente']}"
            )

        nueva_venta = Venta(
            caja_id=caja_id,
            fecha_hora=datetime.now(),
            pagado=pagado,
            referencia=referencia_final,
            metodo_pago=metodo_pago,
            total=0.0,
            ganancia_total=0.0
        )
        sesion.add(nueva_venta)
        sesion.flush()

        ids_productos_afectados = set()

        for item in carrito:
            subtotal = item['subtotal']
            ganancia_item = (item['precio_venta'] - item['costo']) * item['cantidad']

            total_venta += subtotal
            ganancia_venta += ganancia_item
            ids_productos_afectados.add(item['id'])

            detalle = DetalleVenta(
                venta_id=nueva_venta.id,
                producto_id=item['id'],
                cantidad=item['cantidad'],
                precio_unitario=item['precio_venta'],
                costo_unitario=item['costo'],
                subtotal=subtotal
            )
            sesion.add(detalle)

            if not item.get('recuperado'):
                ajustar_stock_producto(sesion, item['id'], -item['cantidad'])

        nueva_venta.total = total_venta
        nueva_venta.ganancia_total = ganancia_venta

        origen_id_pagado = None
        if pagado:
            if caja_id:
                caja = sesion.query(ContabilidadCaja).filter(ContabilidadCaja.id == caja_id).first()
                if caja:
                    if metodo_pago == "Efectivo":
                        caja.ventas_efectivo += total_venta
                    elif metodo_pago == "Nequi":
                        caja.ventas_nequi += total_venta

            if venta_guardada_origen:
                venta_origen_db = sesion.query(Venta).filter(Venta.id == venta_guardada_origen['id']).first()
                if venta_origen_db:
                    fecha_pago_str = datetime.now().strftime("%d-%m-%Y")
                    venta_origen_db.metodo_pago = f"Pagada|{fecha_pago_str}"
                    origen_id_pagado = venta_origen_db.id

        sesion.commit()

        if origen_id_pagado:
            cumplir_notificacion_por_tipo_entidad("VENTA_ANTIGUA", origen_id_pagado)

        for prod_id in ids_productos_afectados:
            evaluar_notificaciones_producto(prod_id)

        return True, "Venta registrada con éxito."

    except Exception as e:
        sesion.rollback()
        return False, f"Error al procesar la venta: {str(e)}"
    finally:
        sesion.close()


def obtener_ventas_pendientes():
    sesion = SessionLocal()
    try:
        ventas = sesion.query(Venta).filter(
            Venta.pagado == False,
            Venta.metodo_pago == "Pendiente"
        ).all()

        lista_ventas = []
        for v in ventas:
            items = []
            for detalle in v.detalles:
                items.append({
                    "id": detalle.producto_id,
                    "nombre": detalle.producto.nombre,
                    "precio_venta": detalle.precio_unitario,
                    "costo": detalle.producto.costo if detalle.producto else 0,
                    "cantidad": detalle.cantidad,
                    "subtotal": detalle.subtotal
                })
            lista_ventas.append({
                "id": v.id,
                "cliente": v.referencia or "Sin Nombre",
                "total": v.total,
                "fecha": v.fecha_hora.strftime("%d/%m/%Y %I:%M %p"),
                "fecha_solo": v.fecha_hora.strftime("%d-%m-%Y"),
                "cantidad_total": sum(item["cantidad"] for item in items),
                "items": items
            })
        return lista_ventas
    finally:
        sesion.close()


def eliminar_venta_pendiente(venta_id):
    """Elimina el registro temporal si se vuelve a guardar un pedido recuperado."""
    sesion = SessionLocal()
    try:
        venta = sesion.query(Venta).filter(Venta.id == venta_id, Venta.pagado == False).first()
        if venta:
            sesion.delete(venta)
            sesion.commit()
            cumplir_notificacion_por_tipo_entidad("VENTA_ANTIGUA", venta_id)
            return True
        return False
    except Exception as e:
        sesion.rollback()
        print(f"Error al liberar venta pendiente: {e}")
        return False
    finally:
        sesion.close()


def registrar_perdida_venta_guardada(venta_id, caja_id=None):
    """Marca una venta guardada como 'Eliminada|fecha' en su turno original y registra la pérdida en la caja actual."""
    from dal.modelos.contabilidad_caja import GastoCaja
    sesion = SessionLocal()
    try:
        venta = sesion.query(Venta).filter(Venta.id == venta_id, Venta.pagado == False).first()
        if not venta:
            return False, "No se encontró el pedido guardado."

        caja_destino = caja_id if caja_id else venta.caja_id
        ref = venta.referencia or "Sin referencia"
        fecha_guardada = venta.fecha_hora.strftime("%d-%m-%Y") if venta.fecha_hora else "N/A"
        fecha_eliminacion = datetime.now().strftime("%d-%m-%Y")

        for det in venta.detalles:
            perdida = GastoCaja(
                caja_id=caja_destino,
                descripcion=f"Venta guardada eliminada (Guardada el {fecha_guardada}) - Ref: {ref}",
                tipo_gasto="Inventario",
                monto=det.costo_unitario * det.cantidad,
                producto_id=det.producto_id,
                cantidad_descontada=det.cantidad
            )
            sesion.add(perdida)

        venta.metodo_pago = f"Eliminada|{fecha_eliminacion}"

        sesion.commit()
        cumplir_notificacion_por_tipo_entidad("VENTA_ANTIGUA", venta_id)
        return True, "Pedido eliminado y registrado como pérdida."
    except Exception as e:
        sesion.rollback()
        return False, f"Error al registrar pérdida: {e}"
    finally:
        sesion.close()