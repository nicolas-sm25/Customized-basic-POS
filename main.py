import sys
import os
import ctypes
import logging
import tkinter.messagebox as messagebox
import customtkinter as ctk
import json
from dal.conexion_DB import inicializar_base_datos, CARPETA_CONFIG, CARPETA_IMAGENES
from ui.ventana_principal import VentanaPrincipal

# --- BLOQUEO DOBLE INSTANCIA ---
mutex_name = "Global\\POS_MiTienda_Mutex_Unico"
mutex = ctypes.windll.kernel32.CreateMutexW(None, False, mutex_name)
if ctypes.windll.kernel32.GetLastError() == 183: 
    messagebox.showerror("Error de Ejecución", "El sistema ya está abierto en otra ventana.")
    sys.exit()

# --- REGISTRO SILENCIOSO DE ERRORES ---
if getattr(sys, 'frozen', False):
    dir_base = os.path.dirname(sys.executable)
else:
    dir_base = os.path.dirname(os.path.abspath(__file__))

log_path = os.path.join(dir_base, "errores_sistema.log")

logging.basicConfig(
    filename=log_path, 
    level=logging.ERROR, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def capturar_error_fatal(exc_type, exc_value, exc_traceback):
    logging.error("Excepción fatal no capturada (Cierre repentino):", exc_info=(exc_type, exc_value, exc_traceback))
    messagebox.showerror("Error Crítico", "El sistema ha detectado un problema grave y debe cerrarse.\n\nEl error ha sido registrado en 'errores_sistema.log'.")
    sys.__excepthook__(exc_type, exc_value, exc_traceback)

sys.excepthook = capturar_error_fatal

# --- CARGA DEL NOMBRE ---
CONFIG_PATH = os.path.join(CARPETA_CONFIG, "config.json")

def cargar_configuracion_basica():
    nombre_tienda = "TIENDA"
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, 'r') as f:
                cfg = json.load(f)
                nombre_tienda = cfg.get("nombre_tienda", nombre_tienda)
        except Exception:
            pass
    return nombre_tienda

# --- ARRANQUE DEL SISTEMA ---
def iniciar_app():
    inicializar_base_datos()
    
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")
    
    nombre_tienda = cargar_configuracion_basica()
    app = VentanaPrincipal(nombre_tienda)
    
    # --- BUSCADOR INTELIGENTE DE ICONO (.ico) ---
    try:
        iconos = [f for f in os.listdir(CARPETA_IMAGENES) if f.lower().endswith('.ico')]
        if iconos:
            ruta_icono = os.path.join(CARPETA_IMAGENES, iconos[0])
            app.iconbitmap(ruta_icono)
    except Exception as e:
        logging.error(f"Error cargando icono: {e}")
            
    app.mainloop()

if __name__ == "__main__":
    iniciar_app()