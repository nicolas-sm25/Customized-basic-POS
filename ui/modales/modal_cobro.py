import customtkinter as ctk
from ui.componentes.creador_componentes import *

class ModalCobro(ctk.CTkToplevel):
    def __init__(self, master, total_actual, callback_procesar):
        super().__init__(master)
        
        self.title("Cobrar Venta")
        self.geometry("400x300")
        self.transient(master.winfo_toplevel())
        self.grab_set()

        # Diseño del pop-up
        frame_modal = nuevo_frame(self)
        frame_modal.pack(expand=True, fill="both", padx=20, pady=20)

        lbl_titulo = nuevo_label(frame_modal, "Seleccione Método de Pago", fuente=FUENTE_TITULOS)
        lbl_titulo.pack(pady=10)

        lbl_monto = nuevo_label(frame_modal, f"Monto a cobrar: {total_actual}", fuente=("Arial", 24, "bold"), color_texto=COLOR_EXITO)
        lbl_monto.pack(pady=20)

        frame_botones = nuevo_frame(frame_modal, color_fondo="transparent")
        frame_botones.pack(pady=10)

        # Botones que llaman la vista principal
        btn_efectivo = nuevo_boton(frame_botones, "Efectivo (Enter)", comando=lambda: callback_procesar("Efectivo", self), color_fondo=COLOR_EXITO, color_hover=COLOR_EXITO_HOVER)
        btn_efectivo.grid(row=0, column=0, padx=10)

        btn_nequi = nuevo_boton(frame_botones, "Nequi", comando=lambda: callback_procesar("Nequi", self), color_fondo="#5e17eb", color_hover="#4a11c0")
        btn_nequi.grid(row=0, column=1, padx=10)

        btn_regresar = nuevo_boton(frame_modal, "Regresar (Esc)", comando=self.destroy, color_fondo=COLOR_FALLO, color_hover=COLOR_FALLO_HOVER)
        btn_regresar.pack(side="bottom", pady=10)

        # Atajos de teclado
        self.bind("<Escape>", lambda event: self.destroy())
        self.bind("<Return>", lambda event: callback_procesar("Efectivo", self))