import sys
import os
import ctypes
import logging
import tkinter.messagebox as messagebox
import customtkinter as ctk
from dal.conexion_DB import inicializar_base_datos
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

# --- CAPTURA DE EXCEPCIONES FATALES ---
def capturar_error_fatal(exc_type, exc_value, exc_traceback):
    logging.error("Excepción fatal no capturada (Cierre repentino):", exc_info=(exc_type, exc_value, exc_traceback))
    
    messagebox.showerror(
        "Error Crítico", 
        "El sistema ha detectado un problema grave y debe cerrarse.\n\n"
        "El error ha sido registrado en 'errores_sistema.log'."
    )
    
    sys.__excepthook__(exc_type, exc_value, exc_traceback)

sys.excepthook = capturar_error_fatal

# --- ARRANQUE DEL SISTEMA ---
def iniciar_app():
    inicializar_base_datos()
    
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")
    
    app = VentanaPrincipal()
    app.mainloop()

if __name__ == "__main__":
    iniciar_app()