from dal.conexion_DB import SessionLocal
from dal.modelos.productos import Producto

from dal.modelos.productos import Producto 

def agregar_producto(nombre, costo, precio_venta, codigo_barras=None, stock=0, es_paquete=False, producto_base_id=None, cantidad_por_paquete=1):
    sesion = SessionLocal()
    try:
        nuevo_prod = Producto(
            nombre=nombre,
            costo=costo,
            precio_venta=precio_venta,
            codigo_barras=codigo_barras,
            stock=stock, 
            es_paquete=es_paquete,
            producto_base_id=producto_base_id,
            cantidad_por_paquete=cantidad_por_paquete
        )
        sesion.add(nuevo_prod)
        sesion.flush()

        if es_paquete and producto_base_id and stock > 0:
            producto_base = sesion.query(Producto).filter(Producto.id == producto_base_id).first()
            if producto_base:
                unidades_a_sumar = stock * cantidad_por_paquete
                producto_base.stock += unidades_a_sumar

                paquetes_vinculados = sesion.query(Producto).filter(Producto.producto_base_id == producto_base.id).all()
                for paquete in paquetes_vinculados:
                    paquete.stock = producto_base.stock // paquete.cantidad_por_paquete

        sesion.commit()
        return True, f"Producto '{nombre}' agregado exitosamente."
    except Exception as e:
        sesion.rollback()
        return False, f"Error al guardar: {str(e)}"
    finally:
        sesion.close()            


def buscar_productos_por_nombre(nombre_parcial):
    
    sesion = SessionLocal()
    
    try:
        productos = sesion.query(Producto).filter(
            Producto.nombre.ilike(f"%{nombre_parcial}%"), 
            Producto.activo == True
        ).all()
        
        return [{
            "id": p.id,
            "nombre": p.nombre,
            "codigo_barras": p.codigo_barras,
            "costo": p.costo,
            "precio_venta": p.precio_venta,
            "stock": p.stock
        } for p in productos]
    except Exception:
        return []
    finally:
        sesion.close()


def buscar_producto_por_codigo(codigo):
    sesion = SessionLocal()
    try:
        producto = sesion.query(Producto).filter(Producto.codigo_barras == codigo, Producto.activo == True).first()
        if producto:
            return {
                "id": producto.id,
                "nombre": producto.nombre,
                "codigo_barras": producto.codigo_barras,
                "costo": producto.costo,
                "precio_venta": producto.precio_venta,
                "stock": producto.stock
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
        
        stock_antiguo = producto.stock
        if stock_nuevo < stock_antiguo:
            return False, "No se puede reducir el stock desde la edición. El stock solo puede aumentar o mantenerse."
        
        diferencia_stock = stock_nuevo - stock_antiguo

        if diferencia_stock > 0:
            if producto.es_paquete and producto.producto_base_id:
                producto_base = sesion.query(Producto).filter(Producto.id == producto.producto_base_id).first()
                if producto_base:
                    producto_base.stock += (diferencia_stock * producto.cantidad_por_paquete)
            else:
                paquetes_vinculados = sesion.query(Producto).filter(Producto.producto_base_id == producto.id).all()
                for paquete in paquetes_vinculados:
                    paquete.stock = (producto.stock + diferencia_stock) // paquete.cantidad_por_paquete
        
        producto.nombre = nombre
        producto.costo = costo
        producto.precio_venta = precio_venta
        producto.codigo_barras = codigo_barras
        producto.stock = stock_nuevo
        
        sesion.commit()
        return True, "Producto actualizado correctamente."
        
    except Exception as e:
        sesion.rollback()
        return False, f"Error interno al intentar actualizar el producto: {str(e)}"
        
    finally:
        sesion.close()


def sincronizar_stock_relacional(sesion, producto_id, cantidad_agregada):
    """
    Ajusta el inventario cuando llega mercancía nueva.
    Se debe llamar ANTES de hacer el sesion.commit() al agregar/editar stock.
    """
    producto_db = sesion.query(Producto).filter(Producto.id == producto_id).first()
    
    if not producto_db:
        return

    if producto_db.es_paquete and producto_db.producto_base_id:
        producto_base = sesion.query(Producto).filter(Producto.id == producto_db.producto_base_id).first()
        if producto_base:
            producto_base.stock += (cantidad_agregada * producto_db.cantidad_por_paquete)
            producto_db.stock = producto_base.stock // producto_db.cantidad_por_paquete

    else:
        producto_db.stock += cantidad_agregada
        paquetes_vinculados = sesion.query(Producto).filter(Producto.producto_base_id == producto_db.id).all()
        for paquete in paquetes_vinculados:
            paquete.stock = producto_db.stock // paquete.cantidad_por_paquete

def obtener_productos_unitarios():
    """Devuelve solo los productos que NO son paquetes para el menú desplegable."""
    sesion = SessionLocal()
    try:
        productos = sesion.query(Producto).filter(Producto.es_paquete == False).all()
        return [{"id": p.id, "nombre": p.nombre} for p in productos]
    finally:
        sesion.close()