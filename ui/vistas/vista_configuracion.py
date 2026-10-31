import customtkinter as ctk
from ui.componentes.configuracion_componentes import ConfiguracionComponentes
from ui.componentes.creador_componentes import *

class VistaConfiguracion(ConfiguracionComponentes):
    def __init__(self, master, callback_cerrar_sesion):
        super().__init__(master)
        self.callback_cerrar_sesion = callback_cerrar_sesion

        # --- TÍTULO ---
        self.lbl_titulo = nuevo_label(self, "Configuración del Sistema", fuente=FUENTE_TITULOS)
        self.lbl_titulo.pack(pady=15)

        # --- CONTENEDOR PRINCIPAL ---
        self.frame_container = nuevo_frame(self, color_fondo="#202020", radio_esquinas=10)
        self.frame_container.pack(fill="both", expand=True, padx=20, pady=10)

        f_contenido = ctk.CTkScrollableFrame(self.frame_container, fg_color="transparent")
        f_contenido.pack(fill="both", expand=True, padx=20, pady=20)

        # --- SECCIÓN: APARIENCIA ---
        nuevo_label(f_contenido, "Apariencia de la Interfaz", fuente=("Arial", 16, "bold"), color_texto="#d4ac0d", poscicion="w").pack(anchor="w", pady=(0, 10))
        
        f_tema = nuevo_frame(f_contenido, color_fondo="#2b2b2b")
        f_tema.pack(fill="x", pady=5, padx=5)
        
        nuevo_label(f_tema, "Tema visual:", fuente=("Arial", 13), poscicion="w").pack(side="left", padx=15, pady=15)
        
        self.combo_tema = ctk.CTkOptionMenu(
            f_tema, 
            values=["Dark", "Light", "System"],
            command=self.cambiar_tema,
            fg_color="#3b3b3b",
            button_color="#4b4b4b",
            button_hover_color="#5b5b5b",
            width=140
        )
        self.combo_tema.pack(side="right", padx=15, pady=15)
        self.combo_tema.set(ctk.get_appearance_mode())

        # --- SECCIÓN: CUENTA Y SESIÓN ---
        nuevo_label(f_contenido, "Control de Sesión", fuente=("Arial", 16, "bold"), color_texto="#d4ac0d", poscicion="w").pack(anchor="w", pady=(25, 10))
        
        f_sesion = nuevo_frame(f_contenido, color_fondo="#2b2b2b")
        f_sesion.pack(fill="x", pady=5, padx=5)
        
        f_info_sesion = nuevo_frame(f_sesion, color_fondo="transparent")
        f_info_sesion.pack(side="left", padx=15, pady=15)
        nuevo_label(f_info_sesion, "Cerrar sesión actual", fuente=("Arial", 13, "bold"), poscicion="w").pack(anchor="w")
        nuevo_label(f_info_sesion, "Volverás a la pantalla de inicio de sesión.", fuente=("Arial", 11), color_texto="#a0a0a0", poscicion="w").pack(anchor="w")

        nuevo_boton(
            f_sesion, 
            "Cerrar Sesión", 
            comando=self.callback_cerrar_sesion, 
            color_fondo=COLOR_FALLO, 
            color_hover=COLOR_FALLO_HOVER,
            ancho=140
        ).pack(side="right", padx=15, pady=15)

    def cambiar_tema(self, nuevo_modo):
        ctk.set_appearance_mode(nuevo_modo)