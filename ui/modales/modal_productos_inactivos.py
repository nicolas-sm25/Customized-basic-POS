import customtkinter as ctk
from ui.componentes.creador_componentes import *
from ui.modales.modal_inventario import ModalConfirmacionEstado

class ModalProductosInactivos:
    def __init__(self, master, productos_inactivos, callback_reactivar):
        self.master = master
        self.callback_reactivar = callback_reactivar
        self.modal = nuevo_modal(master, "Productos Inhabilitados", 600, 500)

        frame_modal = nuevo_frame(self.modal)
        frame_modal.pack(expand=True, fill="both", padx=20, pady=20)

        nuevo_label(frame_modal, "Productos Inhabilitados", fuente=FUENTE_TITULOS).pack(pady=10)
        nuevo_label(frame_modal, "Estos productos no aparecen en las ventas ni búsquedas.", fuente=("Arial", 11), color_texto="#a0a0a0").pack(pady=(0, 10))

        if not productos_inactivos:
            nuevo_label(frame_modal, "No hay productos inhabilitados.", fuente=("Arial", 14, "bold"), color_texto="#a0a0a0").pack(expand=True)
            btn_cerrar = nuevo_boton(frame_modal, "Cerrar (Esc)", comando=self.cerrar_modal, color_fondo=COLOR_FALLO, color_hover=COLOR_FALLO_HOVER)
            btn_cerrar.pack(side="bottom", pady=10)
            self.modal.bind("<Escape>", lambda e: self.cerrar_modal())
            return

        self.scroll_tabla = ctk.CTkScrollableFrame(frame_modal, fg_color="transparent")
        self.scroll_tabla.pack(fill="both", expand=True, pady=10)

        # --- CABECERA ---
        f_enc = nuevo_frame(self.scroll_tabla, color_fondo="#1a1a1a")
        f_enc.pack(fill="x", pady=(0, 5), padx=5)

        cols = [3, 2, 2]
        for i, w in enumerate(cols): f_enc.grid_columnconfigure(i, weight=w, uniform="ina")

        nuevo_label(f_enc, "Producto", fuente=("Arial", 12, "bold"), color_texto="#a0a0a0", poscicion="w").grid(row=0, column=0, sticky="w", padx=10, pady=8)
        nuevo_label(f_enc, "Info", fuente=("Arial", 12, "bold"), color_texto="#a0a0a0", poscicion="center").grid(row=0, column=1, sticky="nsew", pady=8)
        nuevo_label(f_enc, "Acción", fuente=("Arial", 12, "bold"), color_texto="#a0a0a0", poscicion="center").grid(row=0, column=2, sticky="nsew", pady=8)

        # --- FILAS DE PRODUCTOS ---
        for prod in productos_inactivos:
            f_item = nuevo_frame(self.scroll_tabla, color_fondo="#1c1c1c")
            f_item.pack(fill="x", pady=3, padx=5)

            for i, w in enumerate(cols): f_item.grid_columnconfigure(i, weight=w, uniform="ina")

            nuevo_label(f_item, prod['nombre'], fuente=("Arial", 13, "bold"), color_texto="#666666", poscicion="w").grid(row=0, column=0, sticky="w", padx=10, pady=10)
            
            texto_paq = prod['info_paquete'] if prod['info_paquete'] else "Unidad"
            nuevo_label(f_item, texto_paq, fuente=("Arial", 11), color_texto="#666666", poscicion="center").grid(row=0, column=1, sticky="nsew", pady=10)

            f_btn = nuevo_frame(f_item, color_fondo="transparent")
            f_btn.grid(row=0, column=2, sticky="nsew", pady=5)

            nuevo_boton(f_btn, "✓ Reactivar", comando=lambda p_id=prod['id'], p_n=prod['nombre']: self.confirmar_y_reactivar(p_id, p_n), color_fondo=COLOR_EXITO, color_hover=COLOR_EXITO_HOVER, ancho=90).pack(expand=True)

        btn_cerrar = nuevo_boton(frame_modal, "Cerrar (Esc)", comando=self.cerrar_modal, color_fondo=COLOR_FALLO, color_hover=COLOR_FALLO_HOVER)
        btn_cerrar.pack(side="bottom", pady=10)
        self.modal.bind("<Escape>", lambda e: self.cerrar_modal())

    def confirmar_y_reactivar(self, producto_id, nombre_producto):
        # Reutilizamos tu modal de confirmación
        ModalConfirmacionEstado(self.modal, nombre_producto, True, lambda: self.ejecutar_reactivacion(producto_id))

    def ejecutar_reactivacion(self, producto_id):
        self.cerrar_modal()
        self.callback_reactivar(producto_id)

    def cerrar_modal(self):
        self.modal.destroy()