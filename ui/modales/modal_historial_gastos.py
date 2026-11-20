import customtkinter as ctk
from ui.componentes.creador_componentes import *
from bll.gestor_caja import obtener_todos_los_gastos


class ModalHistorialGastos:
    def __init__(self, master):
        self.modal = nuevo_modal(master, "Historial Global de Gastos", 960, 640)
        self.modal.focus_force()

        frame_ppal = nuevo_frame(self.modal)
        frame_ppal.pack(expand=True, fill="both", padx=20, pady=15)

        nuevo_label(frame_ppal, "Historial Global de Gastos", fuente=FUENTE_TITULOS).pack(pady=(0, 10))

        self.gastos = obtener_todos_los_gastos()

        self.frame_contenedor = nuevo_frame(frame_ppal, color_fondo="#202020", radio_esquinas=10)
        self.frame_contenedor.pack(fill="both", expand=True, pady=5)

        self.frame_lista = nuevo_frame(self.frame_contenedor, color_fondo="transparent")
        self.frame_lista.pack(fill="both", expand=True, padx=10, pady=10)

        # --- PAGINACIÓN ---
        self.pagina_actual = 1
        self.items_por_pagina = 8

        self.frame_paginacion = nuevo_frame(self.frame_contenedor, color_fondo="transparent")
        self.frame_paginacion.pack(fill="x", pady=(0, 10))

        self.btn_menos_5 = nuevo_boton(self.frame_paginacion, "<< 5 Pags", comando=lambda: self.cambiar_pagina(-5), ancho=90, color_fondo="#1f538d")
        self.btn_menos_5.pack(side="left", padx=(20, 5))

        self.btn_menos_1 = nuevo_boton(self.frame_paginacion, "< Anterior", comando=lambda: self.cambiar_pagina(-1), ancho=90, color_fondo="#1f538d")
        self.btn_menos_1.pack(side="left", padx=5)

        self.lbl_paginacion = nuevo_label(self.frame_paginacion, "Página 1 / 1", fuente=("Arial", 12, "bold"), color_texto="#a0a0a0")
        self.lbl_paginacion.pack(side="left", expand=True)

        self.btn_mas_5 = nuevo_boton(self.frame_paginacion, "5 Pags >>", comando=lambda: self.cambiar_pagina(5), ancho=90, color_fondo="#1f538d")
        self.btn_mas_5.pack(side="right", padx=(5, 20))

        self.btn_mas_1 = nuevo_boton(self.frame_paginacion, "Siguiente >", comando=lambda: self.cambiar_pagina(1), ancho=90, color_fondo="#1f538d")
        self.btn_mas_1.pack(side="right", padx=5)

        self.renderizar_pagina()

        nuevo_boton(frame_ppal, "Cerrar (Esc)", comando=self.modal.destroy, color_fondo=COLOR_FALLO, color_hover=COLOR_FALLO_HOVER, ancho=140).pack(pady=(10, 0))
        self.modal.bind("<Escape>", lambda e: self.modal.destroy())

    def cambiar_pagina(self, salto):
        nueva_pagina = self.pagina_actual + salto
        if nueva_pagina < 1:
            nueva_pagina = 1
        elif nueva_pagina > getattr(self, 'total_paginas', 1):
            nueva_pagina = getattr(self, 'total_paginas', 1)

        if nueva_pagina != self.pagina_actual:
            self.pagina_actual = nueva_pagina
            self.renderizar_pagina()

    def renderizar_pagina(self):
        for widget in self.frame_lista.winfo_children():
            widget.destroy()

        if not self.gastos:
            nuevo_label(self.frame_lista, "No hay gastos ni bajas de inventario registrados.", fuente=("Arial", 14, "bold"), color_texto="#a0a0a0").pack(expand=True, pady=60)
            self.frame_paginacion.pack_forget()
            return

        self.frame_paginacion.pack(fill="x", pady=(0, 10))
        self.total_paginas = max(1, (len(self.gastos) + self.items_por_pagina - 1) // self.items_por_pagina)
        if self.pagina_actual > self.total_paginas:
            self.pagina_actual = self.total_paginas

        inicio = (self.pagina_actual - 1) * self.items_por_pagina
        gastos_pagina = self.gastos[inicio:inicio + self.items_por_pagina]

        self.lbl_paginacion.configure(text=f"Página {self.pagina_actual} / {self.total_paginas}")
        self.btn_menos_1.configure(state="normal" if self.pagina_actual > 1 else "disabled")
        self.btn_menos_5.configure(state="normal" if self.pagina_actual > 1 else "disabled")
        self.btn_mas_1.configure(state="normal" if self.pagina_actual < self.total_paginas else "disabled")
        self.btn_mas_5.configure(state="normal" if self.pagina_actual < self.total_paginas else "disabled")

        f_enc = nuevo_frame(self.frame_lista, color_fondo="#1a1a1a")
        f_enc.pack(fill="x", pady=(0, 5), padx=5)
        cols = [2, 2, 4, 2, 1, 2]
        for i, w in enumerate(cols):
            f_enc.grid_columnconfigure(i, weight=w, uniform="hg")

        titulos = [("Fecha / Hora", "w"), ("Encargado", "w"), ("Descripción", "w"), ("Producto", "center"), ("Cant.", "center"), ("Monto", "e")]
        for idx, (t, pos) in enumerate(titulos):
            nuevo_label(f_enc, t, fuente=("Arial", 11, "bold"), color_texto="#a0a0a0", poscicion=pos).grid(
                row=0, column=idx, sticky="nsew" if pos == "center" else pos, padx=8, pady=8
            )

        for g in gastos_pagina:
            f = nuevo_frame(self.frame_lista, color_fondo="#2b2b2b")
            f.pack(fill="x", pady=3, padx=5)
            for i, w in enumerate(cols):
                f.grid_columnconfigure(i, weight=w, uniform="hg")

            nuevo_label(f, g['fecha_hora'], fuente=("Arial", 11), poscicion="w").grid(row=0, column=0, sticky="w", padx=8, pady=8)
            nuevo_label(f, g['encargado'], fuente=("Arial", 11, "bold"), color_texto="#d4ac0d", poscicion="w").grid(row=0, column=1, sticky="w", padx=8, pady=8)

            color_desc = "#d4ac0d" if g['tipo'] == "Inventario" else "#ffffff"
            lbl_desc = nuevo_label(f, g['descripcion'], fuente=("Arial", 11), color_texto=color_desc, poscicion="w")
            lbl_desc.configure(wraplength=250, justify="left")
            lbl_desc.grid(row=0, column=2, sticky="w", padx=8, pady=8)

            nuevo_label(f, g['producto'], fuente=("Arial", 11), color_texto="#4fa6ff" if g['producto'] != "-" else "#888888", poscicion="center").grid(row=0, column=3, sticky="nsew", pady=8)
            nuevo_label(f, str(g['cantidad']), fuente=("Arial", 11, "bold"), poscicion="center").grid(row=0, column=4, sticky="nsew", pady=8)
            nuevo_label(f, f"${int(g['monto']):,}".replace(",", "."), fuente=("Arial", 11, "bold"), color_texto=COLOR_FALLO, poscicion="e").grid(row=0, column=5, sticky="e", padx=8, pady=8)