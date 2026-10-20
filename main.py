import customtkinter as ctk
from dal.conexion_DB import inicializar_base_datos
from ui.ventana_principal import VentanaPrincipal

def iniciar_app():
    inicializar_base_datos()
    
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    
    app = VentanaPrincipal()
    app.mainloop()

if __name__ == "__main__":
    iniciar_app()