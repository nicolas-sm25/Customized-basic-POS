import customtkinter as ctk
from ui.componentes.creador_componentes import *

class ModalGuardar:
    def __init__(self, master, callback_guardar):
        self.master = master
        self.modal = nuevo_modal(master, "Guardar Venta en Espera", 450, 300)

        frame_modal = nuevo_frame(self.modal)
        frame_modal.pack(expand=True, fill="both", padx=20, pady=20)

        nuevo_label(frame_modal, "Guardar venta", fuente=FUENTE_TITULOS).pack(pady=10)
        nuevo_label(frame_modal, "Nombre del cliente o referencia:").pack(pady=10)

        self.entry_referencia = nueva_caja_texto(frame_modal, placeholder="Nombre...")
        self.entry_referencia.pack(pady=10)

        self.lbl_error = nuevo_label(frame_modal, "", color_texto=COLOR_FALLO)
        self.lbl_error.pack(pady=5)

        frame_botones = nuevo_frame(frame_modal, color_fondo="transparent")
        frame_botones.pack(pady=10)

        def ejecutar_guardado(event=None):
            referencia = self.entry_referencia.get().strip()
            if not referencia:
                self.lbl_error.configure(text="El nombre no puede estar vacío.")
                return
            callback_guardar(referencia, self)

        nuevo_boton(frame_botones, "Guardar (Enter)", comando=ejecutar_guardado, color_fondo="#d4ac0d", color_hover="#b9770e").grid(row=0, column=0, padx=10)
        nuevo_boton(frame_botones, "Cancelar (Esc)", comando=self.cerrar_modal, color_fondo=COLOR_FALLO, color_hover=COLOR_FALLO_HOVER).grid(row=0, column=1, padx=10)

        self.modal.bind("<Escape>", lambda event: self.cerrar_modal())
        self.entry_referencia.bind("<Escape>", lambda event: self.cerrar_modal())
        self.modal.bind("<Return>", ejecutar_guardado)
        self.entry_referencia.bind("<Return>", ejecutar_guardado)
        
        self.modal.after(50, self.entry_referencia.focus)

    def cerrar_modal(self):
        self.master.focus()
        if hasattr(self.master, 'entry_buscar_prod'):
            self.master.entry_buscar_prod.focus()
        self.modal.destroy()