from dal.conexion_DB import SessionLocal
from dal.modelos.productos import Producto

def agregar_producto(nombre, costo, precio_venta, codigo_barras=None, stock=0):
    sesion = SessionLocal()
    
    try:
        nuevo_producto = Producto(
            nombre=nombre,
            costo=costo,
            precio_venta=precio_venta,
            codigo_barras=codigo_barras,
            stock=stock
        )
        
        sesion.add(nuevo_producto)
        sesion.commit()
        return True, "Producto guardado exitosamente."
        
    except Exception as e:
        sesion.rollback()
        return False, f"Error al guardar en base de datos."
        
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


def actualizar_producto(id_producto, nombre, costo, precio_venta, codigo_barras, stock):
    
    sesion = SessionLocal()
    
    try:
        producto = sesion.query(Producto).filter(Producto.id == id_producto).first()
        
        if not producto:
            return False, "Producto no encontrado en la base de datos."
        
        producto.nombre = nombre
        producto.costo = costo
        producto.precio_venta = precio_venta
        producto.codigo_barras = codigo_barras
        producto.stock = stock
        
        sesion.commit()
        return True, "Producto actualizado correctamente."
        
    except Exception:
        sesion.rollback()
        return False, "Error interno al intentar actualizar el producto."
        
    finally:
        sesion.close()