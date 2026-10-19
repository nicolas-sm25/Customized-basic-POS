from dal.conexion_DB import SessionLocal
from dal.modelos import Producto

def agregar_producto(nombre, costo, precio_venta, codigo_barras=None, stock=0):
    """Crea un producto nuevo y lo guarda en la base de datos."""
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
        
        print(f"Éxito: Producto '{nombre}' guardado en la BD.")
        return nuevo_producto
        
    except Exception as e:
        
        sesion.rollback()
        print(f"Error al guardar producto: {e}")
        return None
        
    finally:
        sesion.close()
        

# ! SOLO ES PARA PRUEBA INICIAL, ACTUALIZAR PARA HACER VENTAS UNIVERSALES   
def procesar_venta_simple(codigo_barras, cantidad=1):
    """Simula una venta rápida buscando por código de barras y restando el stock."""
    sesion = SessionLocal()
    
    try:
        producto = sesion.query(Producto).filter(Producto.codigo_barras == codigo_barras).first()
        
        if not producto:
            print("Error: Producto no encontrado.")
            return False
            
        if producto.stock < cantidad:
            print(f"Alerta: No hay stock suficiente de {producto.nombre}. Stock actual: {producto.stock}")
            return False
            
        producto.stock -= cantidad
        
        sesion.commit()
        
        total_venta = producto.precio_venta * cantidad
        ganancia = (producto.precio_venta - producto.costo) * cantidad
        
        print("\n--- TICKET DE VENTA ---")
        print(f"Producto: {producto.nombre}")
        print(f"Cant: {cantidad} | Total: ${total_venta}")
        print(f"(Ganancia registrada: ${ganancia})")
        print("-----------------------\n")
        
        return True
        
    finally:
        sesion.close()