import customtkinter as ctk
from ui.componentes.creador_componentes import *

class ModalConfirmacionEliminarVenta:
    """Sub-modal exclusivo y coherente para eliminar un pedido."""
    def __init__(self, master, cliente, callback_confirmar):
        self.modal = nuevo_modal(master, "Eliminar Pedido", 420, 220)

        f = nuevo_frame(self.modal)
        f.pack(expand=True, fill="both", padx=20, pady=20)
        
        nuevo_label(f, f"¿Eliminar definitivamente el\npedido de '{cliente}'?", fuente=FUENTE_TITULOS).pack(pady=15)
        
        fb = nuevo_frame(f, color_fondo="transparent")
        fb.pack(pady=10)

        nuevo_boton(fb, "Cancelar (Esc)", comando=self.modal.destroy, color_fondo="#555555", color_hover="#777777").grid(row=0, column=0, padx=10)
        nuevo_boton(fb, "Sí, Eliminar (Enter)", comando=lambda: [self.modal.destroy(), callback_confirmar()], color_fondo=COLOR_FALLO, color_hover=COLOR_FALLO_HOVER).grid(row=0, column=1, padx=10)
        
        self.modal.bind("<Escape>", lambda e: self.modal.destroy())
        self.modal.bind("<Return>", lambda e: [self.modal.destroy(), callback_confirmar()])


class ModalVentasGuardadas:
    def __init__(self, master, ventas_pendientes, callback_recuperar, callback_eliminar):
        self.master = master
        self.modal = nuevo_modal(master, "Ventas Guardadas", 600, 750)
        
        self.ventas_pendientes = ventas_pendientes
        self.callback_recuperar = callback_recuperar
        self.callback_eliminar = callback_eliminar

        frame_modal = nuevo_frame(self.modal)
        frame_modal.pack(expand=True, fill="both", padx=20, pady=20)

        nuevo_label(frame_modal, "Ventas Guardadas", fuente=FUENTE_TITULOS).pack(pady=10)

        if not ventas_pendientes:
            nuevo_label(frame_modal, "No hay ventas guardadas.", fuente=FUENTE_NEGRITA).pack(pady=40)
            btn_cerrar = nuevo_boton(frame_modal, "Cerrar (Esc)", comando=self.cerrar_modal, color_fondo=COLOR_FALLO, color_hover=COLOR_FALLO_HOVER)
            btn_cerrar.pack(side="bottom", pady=10)
            self.modal.bind("<Escape>", lambda e: self.cerrar_modal())
            return

        self.frame_lista = ctk.CTkScrollableFrame(frame_modal, fg_color="transparent")
        self.frame_lista.pack(expand=True, fill="both", pady=10)

        self.var_eliminar = ctk.BooleanVar(value=False)
        self.switch_eliminar = ctk.CTkSwitch(
            frame_modal, 
            text="Modo Eliminación (Borrar Pedidos)",
            command=self.redibujar_lista,
            variable=self.var_eliminar,
            font=("Arial", 12, "bold"),
            progress_color=COLOR_FALLO
        )
        self.switch_eliminar.pack(pady=10)

        self.redibujar_lista()

        # Botón rojo coherente
        btn_cerrar = nuevo_boton(frame_modal, "Cerrar (Esc)", comando=self.cerrar_modal, color_fondo=COLOR_FALLO, color_hover=COLOR_FALLO_HOVER)
        btn_cerrar.pack(side="bottom", pady=10)
        self.modal.bind("<Escape>", lambda e: self.cerrar_modal())

    def cerrar_modal(self):
        self.master.focus()
        if hasattr(self.master, 'entry_buscar_prod'):
            self.master.entry_buscar_prod.focus()
        self.modal.destroy()

    def redibujar_lista(self):
        for widget in self.frame_lista.winfo_children():
            widget.destroy()
        for venta in self.ventas_pendientes:
            self.crear_fila_venta(venta)

    def crear_fila_venta(self, venta):
        f_item = nuevo_frame(self.frame_lista, color_fondo="#3b3b3b")
        f_item.pack(fill="x", pady=5, padx=5)

        f_item.grid_columnconfigure(0, weight=1)
        f_item.grid_columnconfigure(1, minsize=80)
        f_item.grid_columnconfigure(2, minsize=120)
        f_item.grid_columnconfigure(3, minsize=100)

        f_info = nuevo_frame(f_item, color_fondo="transparent")
        f_info.grid(row=0, column=0, sticky="w", padx=10, pady=5)
        nuevo_label(f_info, venta['cliente'], fuente=FUENTE_NEGRITA, poscicion="w").pack(anchor="w")
        nuevo_label(f_info, venta['fecha'], color_texto="#a0a0a0", poscicion="w").pack(anchor="w")

        nuevo_label(f_item, f"{venta['cantidad_total']} art.", color_texto="#a0a0a0").grid(row=0, column=1, sticky="e", padx=5, pady=5)
        nuevo_label(f_item, f"Total: ${int(venta['total']):,}".replace(",", "."), fuente=FUENTE_NEGRITA, color_texto=COLOR_EXITO).grid(row=0, column=2, sticky="e", padx=5, pady=5)

        f_controles = nuevo_frame(f_item, color_fondo="transparent")
        f_controles.grid(row=0, column=3, sticky="e", padx=5, pady=5)

        if self.var_eliminar.get():
            nuevo_boton(f_controles, "X", comando=lambda v=venta: self.confirmar_eliminacion(v), color_fondo=COLOR_FALLO, color_hover=COLOR_FALLO_HOVER, ancho=40).pack(side="right", padx=2)
        else:
            nuevo_boton(f_controles, "Recuperar", comando=lambda v=venta: [self.cerrar_modal(), self.callback_recuperar(v)], color_fondo=COLOR_EXITO, color_hover=COLOR_EXITO_HOVER, ancho=90).pack(side="right", padx=2)

    def confirmar_eliminacion(self, venta):
        ModalConfirmacionEliminarVenta(self.modal, venta['cliente'], lambda: self.ejecutar_eliminacion(venta))
        
    def ejecutar_eliminacion(self, venta):
        self.callback_eliminar(venta['id'])
        self.ventas_pendientes = [v for v in self.ventas_pendientes if v['id'] != venta['id']]
        if not self.ventas_pendientes:
            self.cerrar_modal()
        else:
            self.redibujar_lista()