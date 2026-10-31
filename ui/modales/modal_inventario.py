import customtkinter as ctk
from ui.componentes.creador_componentes import *

class ModalConfirmacionEstado:
    def __init__(self, master, nombre_producto, es_activacion, callback_confirmar):
        self.master = master
        accion_texto = "Reactivar" if es_activacion else "Desactivar"
        self.modal = nuevo_modal(master, f"Confirmar {accion_texto}", 550, 250)

        frame_modal = nuevo_frame(self.modal)
        frame_modal.pack(expand=True, fill="both", padx=20, pady=20)
        
        if es_activacion:
            pregunta = f"¿Reactivar '{nombre_producto}'?\n(Volverá a estar disponible en las ventas)"
            color_btn = COLOR_EXITO
            color_hover = COLOR_EXITO_HOVER
            texto_btn = "Sí, Reactivar (Enter)"
        else:
            pregunta = f"¿Desactivar '{nombre_producto}'?\n(Dejará de aparecer en las ventas)"
            color_btn = COLOR_FALLO
            color_hover = COLOR_FALLO_HOVER
            texto_btn = "Sí, Desactivar (Enter)"

        nuevo_label(frame_modal, pregunta, fuente=FUENTE_TITULOS).pack(pady=20)
        
        frame_botones = nuevo_frame(frame_modal)
        frame_botones.pack(pady=10)

        nuevo_boton(frame_botones, "Cancelar (Esc)", comando=self.cerrar_modal, color_fondo="#555555", color_hover="#777777").grid(row=0, column=0, padx=20)

        def ejecutar():
            self.modal.destroy()
            callback_confirmar()

        nuevo_boton(frame_botones, texto_btn, comando=ejecutar, color_fondo=color_btn, color_hover=color_hover).grid(row=0, column=1, padx=20)

        self.modal.bind("<Escape>", lambda event: self.cerrar_modal())
        self.modal.bind("<Return>", lambda event: ejecutar())

    def cerrar_modal(self):
        self.modal.destroy()