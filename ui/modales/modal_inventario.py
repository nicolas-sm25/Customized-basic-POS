import customtkinter as ctk
from ui.componentes.creador_componentes import *

class ModalConfirmacionEstado(ctk.CTkToplevel):
    def __init__(self, master, nombre_producto, es_activacion, callback_confirmar):
        super().__init__(master)
        
        accion_texto = "Reactivar" if es_activacion else "Desactivar"
        self.title(f"Confirmar {accion_texto}")
        self.geometry("450x250")
        self.transient(master.winfo_toplevel()) 
        self.grab_set()

        frame_modal = nuevo_frame(self)
        frame_modal.pack(expand=True, fill="both", padx=20, pady=20)
        
        if es_activacion:
            pregunta = f"¿Reactivar '{nombre_producto}'?\n(Volverá a estar disponible en las ventas)"
            color_btn = COLOR_EXITO
            color_hover = COLOR_EXITO_HOVER
            texto_btn = "Sí, Reactivar"
        else:
            pregunta = f"¿Desactivar '{nombre_producto}'?\n(Dejará de aparecer en las ventas)"
            color_btn = COLOR_FALLO
            color_hover = COLOR_FALLO_HOVER
            texto_btn = "Sí, Desactivar"

        lbl_pregunta = nuevo_label(frame_modal, pregunta, fuente=FUENTE_TITULOS)
        lbl_pregunta.pack(pady=20)
        
        frame_botones = nuevo_frame(frame_modal)
        frame_botones.pack(pady=10)

        btn_regresar = nuevo_boton(frame_botones, "Cancelar", comando=self.destroy, color_fondo="#555555", color_hover="#777777")
        btn_regresar.grid(row=0, column=0, padx=20)

        def ejecutar():
            self.destroy()
            callback_confirmar()

        btn_accion = nuevo_boton(frame_botones, texto_btn, comando=ejecutar, color_fondo=color_btn, color_hover=color_hover)
        btn_accion.grid(row=0, column=1, padx=20)

        self.bind("<Escape>", lambda event: self.destroy())
        self.bind("<Return>", lambda event: ejecutar())