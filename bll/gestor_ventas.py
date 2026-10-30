from dal.conexion_DB import SessionLocal
from dal.modelos.ventas import Venta, DetalleVenta
from dal.modelos.productos import Producto
from dal.modelos.contabilidad_caja import ContabilidadCaja
from datetime import datetime

def registrar_venta(carrito, metodo_pago, caja_id, nombre_cliente="Mostrador", pagado=True):
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

            # 3. Descontar el stock (Solo si la venta está pagada, opcional según reglas de negocio)
            producto_db = sesion.query(Producto).filter(Producto.id == item['id']).first()
            if producto_db:
                producto_db.stock -= item['cantidad']

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