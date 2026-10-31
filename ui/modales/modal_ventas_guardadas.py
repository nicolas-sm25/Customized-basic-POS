import customtkinter as ctk
from ui.componentes.creador_componentes import *

class ModalVentasGuardadas(ctk.CTkToplevel):
    def __init__(self, master, ventas_pendientes, callback_recuperar):
        super().__init__(master)
        
        self.title("Ventas en Espera")
        self.geometry("550x750")
        self.transient(master.winfo_toplevel())
        self.grab_set()

        frame_modal = nuevo_frame(self)
        frame_modal.pack(expand=True, fill="both", padx=20, pady=20)

        lbl_titulo = nuevo_label(frame_modal, "Recuperar Venta", fuente=FUENTE_TITULOS)
        lbl_titulo.pack(pady=10)

        if not ventas_pendientes:
            lbl_vacio = nuevo_label(frame_modal, "No hay ventas guardadas.", fuente=FUENTE_NEGRITA)
            lbl_vacio.pack(pady=40)
            btn_cerrar = nuevo_boton(frame_modal, "Regresar", comando=self.destroy)
            btn_cerrar.pack(side="bottom", pady=10)
            return

        self.frame_lista = ctk.CTkScrollableFrame(frame_modal, fg_color="transparent")
        self.frame_lista.pack(expand=True, fill="both", pady=10)

        for venta in ventas_pendientes:
            self.crear_fila_venta(venta, callback_recuperar)

        btn_cerrar = nuevo_boton(frame_modal, "Cerrar (Esc)", comando=self.destroy, color_fondo=COLOR_FALLO, color_hover=COLOR_FALLO_HOVER)
        btn_cerrar.pack(side="bottom", pady=10)
        self.bind("<Escape>", lambda event: self.destroy())

    def crear_fila_venta(self, venta, callback_recuperar):
        f_item = nuevo_frame(self.frame_lista, color_fondo="#3b3b3b")
        f_item.pack(fill="x", pady=5, padx=5)

        # Columnas
        f_item.grid_columnconfigure(0, weight=1)
        f_item.grid_columnconfigure(1, minsize=80)
        f_item.grid_columnconfigure(2, minsize=120)
        f_item.grid_columnconfigure(3, minsize=100)

        # Columna 0: Cliente y Fecha
        f_info = nuevo_frame(f_item, color_fondo="transparent")
        f_info.grid(row=0, column=0, sticky="w", padx=10, pady=5)
        lbl_cliente = nuevo_label(f_info, venta['cliente'], fuente=FUENTE_NEGRITA, poscicion="w")
        lbl_cliente.pack(anchor="w")
        lbl_fecha = nuevo_label(f_info, venta['fecha'], color_texto="#a0a0a0", poscicion="w")
        lbl_fecha.pack(anchor="w")

        # Columna 1: Cantidad de artículos
        lbl_cant = nuevo_label(f_item, f"{venta['cantidad_total']} art.", color_texto="#a0a0a0")
        lbl_cant.grid(row=0, column=1, sticky="e", padx=5, pady=5)

        # Columna 2: Total
        lbl_total = nuevo_label(f_item, f"Total: ${int(venta['total']):,}".replace(",", "."), fuente=FUENTE_NEGRITA, color_texto=COLOR_EXITO)
        lbl_total.grid(row=0, column=2, sticky="e", padx=5, pady=5)

        # Columna 3: Controles
        f_controles = nuevo_frame(f_item, color_fondo="transparent")
        f_controles.grid(row=0, column=3, sticky="e", padx=5, pady=5)

        # Recuperar carrito
        btn_recuperar = nuevo_boton(
            f_controles,
            "Recuperar",
            comando=lambda v=venta: [self.destroy(), callback_recuperar(v)],
            color_fondo=COLOR_EXITO,
            color_hover=COLOR_EXITO_HOVER,
            ancho=90
        )
        btn_recuperar.pack(side="right", padx=2)