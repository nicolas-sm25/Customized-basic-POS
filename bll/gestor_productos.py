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