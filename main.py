from dal.conexion_DB import inicializar_base_datos, SessionLocal
from bll.gestor_productos import agregar_producto, procesar_venta_simple
from dal.modelos import Producto

def simular_sistema():
    
    print("Iniciando sistema POS...")
    inicializar_base_datos()
    
    sesion = SessionLocal()
    hay_productos = sesion.query(Producto).first()
    sesion.close()
    
    if not hay_productos:
        print("\n--- Registrando Inventario Inicial ---")
        agregar_producto(
            nombre="Chocoramo", 
            costo=1500, 
            precio_venta=2500, 
            codigo_barras="7701234567890", 
            stock=10
        )
        agregar_producto(
            nombre="Gansito", 
            costo=1200, 
            precio_venta=2000, 
            codigo_barras="7700987654321", 
            stock=5
        )
    else:
        print("La base de datos ya tiene productos registrados.")

    print("\n--- Simulando paso por caja ---")
    codigo_escaneado = "7701234567890"
    
    sesion = SessionLocal()
    chocoramo_antes = sesion.query(Producto).filter_by(codigo_barras=codigo_escaneado).first()
    print(f"Stock antes de la venta: {chocoramo_antes.stock}")
    sesion.close()
    
    procesar_venta_simple(codigo_barras=codigo_escaneado, cantidad=1)
    
    sesion = SessionLocal()
    chocoramo_despues = sesion.query(Producto).filter_by(codigo_barras=codigo_escaneado).first()
    print(f"Stock después de la venta: {chocoramo_despues.stock}")
    sesion.close()

if __name__ == "__main__":
    simular_sistema()