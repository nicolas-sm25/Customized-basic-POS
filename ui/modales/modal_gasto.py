import customtkinter as ctk
from ui.componentes.creador_componentes import *
from bll.gestor_caja import registrar_gasto

class ModalGasto:
    def __init__(self, master, caja_id, callback_confirmar):
        self.master = master
        self.modal = nuevo_modal(master, "Registrar Gasto Rápido", 450, 350)
        self.caja_id = caja_id
        self.callback_confirmar = callback_confirmar

        frame_modal = nuevo_frame(self.modal)
        frame_modal.pack(expand=True, fill="both", padx=20, pady=20)
        
        nuevo_label(frame_modal, "Registrar Gasto", fuente=FUENTE_TITULOS).pack(pady=10)
        
        self.entry_desc = nueva_caja_texto(frame_modal, placeholder="Descripción (Ej: Pago a proveedor)")
        self.entry_desc.pack(pady=10, fill="x", padx=20)
        
        self.entry_monto = nueva_caja_texto(frame_modal, placeholder="Monto del gasto")
        self.entry_monto.pack(pady=10, fill="x", padx=20)
        
        self.lbl_mensaje = nuevo_label(frame_modal, "")
        self.lbl_mensaje.pack(pady=5)
        
        frame_botones = nuevo_frame(frame_modal)
        frame_botones.pack(pady=10)

        nuevo_boton(frame_botones, "Guardar (Enter)", comando=self.procesar_gasto, color_fondo=COLOR_EXITO, color_hover=COLOR_EXITO_HOVER).grid(row=0, column=0, padx=10)
        nuevo_boton(frame_botones, "Cancelar (Esc)", comando=self.cerrar_modal, color_fondo=COLOR_FALLO, color_hover=COLOR_FALLO_HOVER).grid(row=0, column=1, padx=10)

        # Atajos y Cadena de Foco
        self.entry_monto.bind("<KeyRelease>", self.formatear_moneda)
        self.entry_desc.bind("<Return>", lambda e: self.entry_monto.focus())
        self.entry_monto.bind("<Return>", lambda e: self.procesar_gasto())
        
        self.entry_desc.bind("<Escape>", lambda e: self.cerrar_modal())
        self.entry_monto.bind("<Escape>", lambda e: self.cerrar_modal())
        self.modal.bind("<Escape>", lambda e: self.cerrar_modal())
        
        self.modal.after(50, self.entry_desc.focus)

    def cerrar_modal(self):
        """Elimina el modal y devuelve el foco seguro, evitando el cursor fantasma."""
        self.master.focus()
        if hasattr(self.master, 'entry_buscar_prod'):
            self.master.entry_buscar_prod.focus()
        self.modal.destroy()

    def formatear_moneda(self, event=None):
        texto_limpio = ''.join(filter(str.isdigit, self.entry_monto.get().replace(".", "")))
        self.entry_monto.delete(0, 'end')
        if texto_limpio:
            self.entry_monto.insert(0, f"{int(texto_limpio):,}".replace(",", "."))

    def procesar_gasto(self):
        desc = self.entry_desc.get().strip()
        monto_str = self.entry_monto.get().replace(".", "").strip()
        
        if not desc or not monto_str:
            self.lbl_mensaje.configure(text="Ingrese descripción y monto.", text_color=COLOR_FALLO)
            return
        try:
            exito, msj = registrar_gasto(self.caja_id, desc, float(monto_str))
            self.cerrar_modal()
            self.callback_confirmar(exito, msj)
        except ValueError:
            self.lbl_mensaje.configure(text="Monto inválido.", text_color=COLOR_FALLO)