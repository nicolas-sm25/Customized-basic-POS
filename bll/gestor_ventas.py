from dal.conexion_DB import SessionLocal
from dal.modelos.ventas import Venta, DetalleVenta
from dal.modelos.productos import Producto
from dal.modelos.contabilidad_caja import ContabilidadCaja
from datetime import datetime

def registrar_venta(carrito, metodo_pago, caja_id, nombre_cliente= None, pagado=True):
    """
    Guarda la venta, sus detalles, descuenta inventario y actualiza el saldo de la caja.
    """
    sesion = SessionLocal()

    try:
        total_venta = 0.0
        ganancia_venta = 0.0

        nueva_venta = Venta(
            caja_id=caja_id,
            fecha_hora=datetime.now(),
            pagado=pagado,
            referencia=nombre_cliente,
            metodo_pago=metodo_pago,
            total=0.0, 
            ganancia_total=0.0
        )
        sesion.add(nueva_venta)
        sesion.flush()

        for item in carrito:
            subtotal = item['subtotal']

            ganancia_item = (item['precio_venta'] - item['costo']) * item['cantidad']
            
            total_venta += subtotal
            ganancia_venta += ganancia_item

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
                producto_db = sesion.query(Producto).filter(Producto.id == item['id']).first()
                
                if producto_db:
                    if producto_db.es_paquete and producto_db.producto_base_id:
                        producto_base = sesion.query(Producto).filter(Producto.id == producto_db.producto_base_id).first()
                        if producto_base:
                            producto_base.stock -= (item['cantidad'] * producto_db.cantidad_por_paquete)
                            producto_db.stock = producto_base.stock // producto_db.cantidad_por_paquete

                    else:
                        producto_db.stock -= item['cantidad']

                        paquetes_vinculados = sesion.query(Producto).filter(Producto.producto_base_id == producto_db.id).all()
                        for paquete in paquetes_vinculados:
                            paquete.stock = producto_db.stock // paquete.cantidad_por_paquete

        nueva_venta.total = total_venta
        nueva_venta.ganancia_total = ganancia_venta

        if pagado and caja_id:
            caja = sesion.query(ContabilidadCaja).filter(ContabilidadCaja.id == caja_id).first()
            if caja:
                if metodo_pago == "Efectivo":
                    caja.ventas_efectivo += total_venta
                elif metodo_pago == "Nequi":
                    caja.ventas_nequi += total_venta

        sesion.commit()
        return True, "Venta registrada con éxito."

    except Exception as e:
        sesion.rollback()
        return False, f"Error al procesar la venta: {str(e)}"
    finally:
        sesion.close()

def obtener_ventas_pendientes():

    sesion = SessionLocal()

    try:
        ventas = sesion.query(Venta).filter(Venta.pagado == False).all()
        
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
                "cantidad_total": sum(item["cantidad"] for item in items),
                "items": items
            })
        return lista_ventas
    finally:
        sesion.close()

def eliminar_venta_pendiente(venta_id):
    """Borra la venta pendiente y devuelve el stock a los productos."""

    sesion = SessionLocal()

    try:
        venta = sesion.query(Venta).filter(Venta.id == venta_id).first()
        if venta:
            sesion.delete(venta)
            sesion.commit()
            return True

    except Exception as e:
        sesion.rollback()
        return False
    finally:
        sesion.close()