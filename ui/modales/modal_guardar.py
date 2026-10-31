import customtkinter as ctk
from ui.componentes.creador_componentes import *

class ModalGuardar(ctk.CTkToplevel):
    def __init__(self, master, callback_guardar):
        super().__init__(master)
        
        self.title("Guardar Venta en Espera")
        self.geometry("450x300")
        self.transient(master.winfo_toplevel())
        self.grab_set()

        # Diseño del pop-up
        frame_modal = nuevo_frame(self)
        frame_modal.pack(expand=True, fill="both", padx=20, pady=20)

        lbl_titulo = nuevo_label(frame_modal, "Guardar venta", fuente=FUENTE_TITULOS)
        lbl_titulo.pack(pady=10)

        lbl_instruccion = nuevo_label(frame_modal, "Nombre del cliente o referencia:")
        lbl_instruccion.pack(pady=10)

        self.entry_referencia = nueva_caja_texto(frame_modal, placeholder="Nombre...")
        self.entry_referencia.pack(pady=10)
        self.after(5, self.entry_referencia.focus)

        self.lbl_error = nuevo_label(frame_modal, "", color_texto=COLOR_FALLO)
        self.lbl_error.pack(pady=5)

        frame_botones = nuevo_frame(frame_modal, color_fondo="transparent")
        frame_botones.pack(pady=10)

        # Validación interna
        def ejecutar_guardado(event=None):
            referencia = self.entry_referencia.get().strip()
            if not referencia:
                self.lbl_error.configure(text="El nombre no puede estar vacío.")
                return
            callback_guardar(referencia, self)

        # Botones
        btn_guardar = nuevo_boton(
            frame_botones, 
            "Guardar (Enter)", 
            comando=ejecutar_guardado, 
            color_fondo="#d4ac0d", 
            color_hover="#b9770e"
        )
        btn_guardar.grid(row=0, column=0, padx=10)

        btn_cancelar = nuevo_boton(
            frame_botones, 
            "Cancelar (Esc)", 
            comando=self.destroy, 
            color_fondo=COLOR_FALLO, 
            color_hover=COLOR_FALLO_HOVER
        )
        btn_cancelar.grid(row=0, column=1, padx=10)

        # Atajos de teclado
        self.bind("<Escape>", lambda event: self.destroy())
        self.bind("<Return>", ejecutar_guardado)