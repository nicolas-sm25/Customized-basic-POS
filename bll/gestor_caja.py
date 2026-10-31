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
def abrir_caja(base_efectivo, usuario_id = None):
    """Crea un nuevo registro de caja y lo marca como abierto."""
    
    sesion = SessionLocal()
    
    try:

        if obtener_caja_abierta():
            return False, "Ya existe una caja abierta. Debe cerrarla primero."
        
        nueva_caja = ContabilidadCaja(
            base_efectivo=base_efectivo,
            usuario_id=usuario_id,
            abierta = True
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
        
from dal.modelos.contabilidad_caja import GastoCaja
from dal.modelos.ventas import Venta

def registrar_gasto(caja_id, descripcion, monto):
    sesion = SessionLocal()
    try:
        caja = sesion.query(ContabilidadCaja).filter(ContabilidadCaja.id == caja_id).first()
        if not caja:
            return False, "Caja no encontrada."
            
        nuevo_gasto = GastoCaja(caja_id=caja_id, descripcion=descripcion, monto=monto)
        caja.gastos_totales += monto
        
        sesion.add(nuevo_gasto)
        sesion.commit()
        return True, "Gasto registrado."
    except Exception as e:
        sesion.rollback()
        return False, str(e)
    finally:
        sesion.close()

def obtener_resumen_caja(caja_id):
    """Devuelve los totales calculados antes de cerrar la caja."""
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
            "efectivo_esperado": caja.base_efectivo + caja.ventas_efectivo - caja.gastos_totales
        }
    finally:
        sesion.close()

def cerrar_caja_definitiva(caja_id, efectivo_fisico, diferencia):
    """Guarda los resultados físicos y marca la caja como cerrada."""
    sesion = SessionLocal()
    try:
        caja = sesion.query(ContabilidadCaja).filter(ContabilidadCaja.id == caja_id).first()
        if caja:
            caja.abierta = False
            caja.fecha_cierre = datetime.now()
            caja.total_efectivo_cierre = efectivo_fisico
            caja.diferencia = diferencia

            resumen = obtener_resumen_caja(caja_id)
            if resumen:
                caja.costos_totales = resumen['costos']
                caja.ganancia_total = resumen['ganancia_bruta']
            
            sesion.commit()
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
            
            fecha_cierre_str = c.fecha_cierre.strftime("%d/%m/%Y %I:%M %p") if c.fecha_cierre else "En curso..."
            
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
                "estado": "Abierta" if c.abierta else "Cerrada"
            })
        return resultado
    finally:
        sesion.close()