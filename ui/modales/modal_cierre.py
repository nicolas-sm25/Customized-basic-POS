import customtkinter as ctk
from ui.componentes.creador_componentes import *

class ModalCierre(ctk.CTkToplevel):
    def __init__(self, master, callback_confirmar):
        super().__init__(master)
        
        self.title("Confirmar Acción")
        self.geometry("450x250")
        self.transient(master.winfo_toplevel()) 
        self.grab_set()

        # Diseño del pop-up
        frame_modal = nuevo_frame(self)
        frame_modal.pack(expand=True, fill="both", padx=20, pady=20)
        
        lbl_pregunta = nuevo_label(frame_modal, "¿Seguro que quieres cerrar la caja?", fuente=FUENTE_TITULOS)
        lbl_pregunta.pack(pady=30)
        
        frame_botones = nuevo_frame(frame_modal)
        frame_botones.pack(pady=10)

        btn_regresar = nuevo_boton(frame_botones, "Regresar", comando=self.destroy, color_fondo=COLOR_EXITO, color_hover=COLOR_EXITO_HOVER)
        btn_regresar.grid(row=0, column=0, padx=20)

        def ejecutar():
            self.destroy()
            callback_confirmar()

        btn_cerrar = nuevo_boton(frame_botones, "Sí, Cerrar Caja", comando=ejecutar, color_fondo=COLOR_FALLO, color_hover=COLOR_FALLO_HOVER)
        btn_cerrar.grid(row=0, column=1, padx=20)

        # Atajos de teclado
        self.bind("<Escape>", lambda event: self.destroy())
        self.bind("<Return>", lambda event: self.destroy())