from datetime import datetime
from dal.conexion_DB import SessionLocal
from dal.modelos.contabilidad_caja import ContabilidadCaja


# --- VERIFICAR SI LA CAJA ESTÁ ABIERTA ---
def obtener_caja_abierta():
    try:
        sesion = SessionLocal() 
        caja = sesion.query(ContabilidadCaja).filter(ContabilidadCaja.abierta == True).first()
        sesion.close()
        return caja

    except Exception as e:
        print(f"Error crítico al consultar caja: {e}")
        return None
    

# --- INICIAR CAJA ---
def abrir_caja(base_efectivo):
    """Crea un nuevo registro de caja y lo marca como abierto."""
    
    sesion = SessionLocal()
    
    try:

        if obtener_caja_abierta():
            return False, "Ya existe una caja abierta. Debe cerrarla primero."
        
        nueva_caja = ContabilidadCaja(
            base_efectivo=base_efectivo
        )
        sesion.add(nueva_caja)
        sesion.commit()
        return True, "Caja abierta exitosamente."
        
    except Exception as e:
        sesion.rollback()
        return False, f"Error en la base de datos al abrir caja: {str(e)}"
    
    
# --- CERRAR CAJA ---    
def cerrar_caja():
    sesion = SessionLocal()
    try:
        cajas_abiertas = sesion.query(ContabilidadCaja).filter(ContabilidadCaja.abierta == True).all()
        
        if not cajas_abiertas:
            return False, "No hay ninguna caja abierta en este momento."
        
        for caja in cajas_abiertas:
            caja.abierta = False
            caja.fecha_cierre = datetime.now()
            
        sesion.commit()
        return True, "Caja cerrada exitosamente."
        
    except Exception as e:
        sesion.rollback()
        return False, f"Error al cerrar la caja: {str(e)}"
    finally:
        sesion.close()