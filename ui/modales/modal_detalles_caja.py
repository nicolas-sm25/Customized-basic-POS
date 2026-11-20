import customtkinter as ctk
from ui.componentes.creador_componentes import *
from bll.gestor_caja import obtener_resumen_caja, obtener_detalles_turno


class ModalDetalleVentaIndividual:
    """Sub-modal con el desglose de productos de una venta específica."""
    def __init__(self, master, venta, titulo_extra=None):
        titulo = titulo_extra or f"Detalle Venta #{venta['id']}"
        self.modal = nuevo_modal(master, titulo, 750, 570)
        self.modal.focus_force()

        frame_ppal = nuevo_frame(self.modal)
        frame_ppal.pack(expand=True, fill="both", padx=20, pady=15)

        subtitulo = f"{titulo}  |  Hora: {venta['hora']}"
        if "metodo_pago" in venta:
            subtitulo += f"  |  Pago: {venta['metodo_pago']}"
        nuevo_label(frame_ppal, subtitulo, fuente=("Arial", 15, "bold"), color_texto="#4fa6ff").pack(pady=(0, 4))

        if venta.get("es_guardada_anterior"):
            nuevo_label(
                frame_ppal,
                f"Venta guardada el {venta['fecha_guardada']}  (Ref: {venta['referencia_guardada']})",
                fuente=("Arial", 12, "bold"),
                color_texto="#d4ac0d"
            ).pack(pady=(0, 8))

        scroll = ctk.CTkScrollableFrame(frame_ppal, fg_color="#202020")
        scroll.pack(fill="both", expand=True, pady=5)

        f_enc = nuevo_frame(scroll, color_fondo="#1a1a1a")
        f_enc.pack(fill="x", pady=(0, 5), padx=5)
        cols = [4, 1, 2, 2]
        for i, w in enumerate(cols):
            f_enc.grid_columnconfigure(i, weight=w, uniform="det_prod")

        headers = [("Producto", "w"), ("Cant.", "center"), ("Precio Unit.", "e"), ("Subtotal", "e")]
        for idx, (texto, pos) in enumerate(headers):
            anclaje = "nsew" if pos == "center" else pos
            nuevo_label(f_enc, texto, fuente=("Arial", 12, "bold"), color_texto="#a0a0a0", poscicion=pos).grid(
                row=0, column=idx, sticky=anclaje, padx=10, pady=6
            )

        for item in venta.get("detalles", []):
            f = nuevo_frame(scroll, color_fondo="#2b2b2b")
            f.pack(fill="x", pady=3, padx=5)
            for i, w in enumerate(cols):
                f.grid_columnconfigure(i, weight=w, uniform="det_prod")

            nuevo_label(f, item["producto"], fuente=("Arial", 12, "bold"), color_texto="#ffffff", poscicion="w").grid(
                row=0, column=0, sticky="w", padx=10, pady=8
            )
            nuevo_label(f, str(item["cantidad"]), fuente=("Arial", 12), poscicion="center").grid(
                row=0, column=1, sticky="nsew", pady=8
            )
            nuevo_label(f, f"${int(item['precio_unitario']):,}".replace(",", "."), fuente=("Arial", 12), color_texto="#cccccc", poscicion="e").grid(
                row=0, column=2, sticky="e", padx=10, pady=8
            )
            nuevo_label(f, f"${int(item['subtotal']):,}".replace(",", "."), fuente=("Arial", 12, "bold"), color_texto=COLOR_EXITO, poscicion="e").grid(
                row=0, column=3, sticky="e", padx=10, pady=8
            )

        nuevo_label(
            frame_ppal,
            f"Total: ${int(venta['total']):,}".replace(",", "."),
            fuente=("Arial", 16, "bold"),
            color_texto=COLOR_EXITO,
            poscicion="e"
        ).pack(fill="x", pady=(8, 4), padx=5)

        nuevo_boton(frame_ppal, "Cerrar (Esc)", comando=self.modal.destroy, color_fondo=COLOR_FALLO, color_hover=COLOR_FALLO_HOVER, ancho=140).pack(pady=(4, 0))
        self.modal.bind("<Escape>", lambda e: self.modal.destroy())


class ModalVentasGuardadasTurno:
    """Modal paginado con las ventas guardadas del turno, su estado y fecha de pago si aplica."""
    def __init__(self, master, caja, ventas_guardadas):
        self.modal = nuevo_modal(master, f"Ventas Guardadas del Turno - {caja['encargado']} - {caja['fecha_apertura']}", 920, 580)
        self.modal.focus_force()
        self.ventas_guardadas = ventas_guardadas

        frame_ppal = nuevo_frame(self.modal)
        frame_ppal.pack(expand=True, fill="both", padx=20, pady=15)

        nuevo_label(
            frame_ppal,
            f"Ventas Guardadas del Día ({len(ventas_guardadas)})",
            fuente=("Arial", 16, "bold"),
            color_texto="#d4ac0d",
            poscicion="w"
        ).pack(fill="x", pady=(0, 8))

        self.frame_contenedor = nuevo_frame(frame_ppal, color_fondo="#202020", radio_esquinas=10)
        self.frame_contenedor.pack(fill="both", expand=True, pady=(0, 10))

        self.frame_lista = nuevo_frame(self.frame_contenedor, color_fondo="transparent")
        self.frame_lista.pack(fill="both", expand=True, padx=10, pady=10)

        # --- PAGINACIÓN ---
        self.pagina_actual = 1
        self.items_por_pagina = 7

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

        nuevo_boton(frame_ppal, "Cerrar (Esc)", comando=self.modal.destroy, color_fondo=COLOR_FALLO, color_hover=COLOR_FALLO_HOVER, ancho=140).pack()
        self.modal.bind("<Escape>", lambda e: self.modal.destroy())

    def cambiar_pagina(self, salto):
        nueva = self.pagina_actual + salto
        if nueva < 1:
            nueva = 1
        elif nueva > getattr(self, 'total_paginas', 1):
            nueva = getattr(self, 'total_paginas', 1)

        if nueva != self.pagina_actual:
            self.pagina_actual = nueva
            self.renderizar_pagina()

    def renderizar_pagina(self):
        for w in self.frame_lista.winfo_children():
            w.destroy()

        if not self.ventas_guardadas:
            nuevo_label(self.frame_lista, "No quedaron ventas guardadas en este turno.", fuente=("Arial", 14, "bold"), color_texto="#a0a0a0").pack(expand=True, pady=60)
            self.frame_paginacion.pack_forget()
            return

        self.frame_paginacion.pack(fill="x", pady=(0, 10))
        self.total_paginas = max(1, (len(self.ventas_guardadas) + self.items_por_pagina - 1) // self.items_por_pagina)
        if self.pagina_actual > self.total_paginas:
            self.pagina_actual = self.total_paginas

        inicio = (self.pagina_actual - 1) * self.items_por_pagina
        pagina_items = self.ventas_guardadas[inicio:inicio + self.items_por_pagina]

        self.lbl_paginacion.configure(text=f"Página {self.pagina_actual} / {self.total_paginas}")
        self.btn_menos_1.configure(state="normal" if self.pagina_actual > 1 else "disabled")
        self.btn_menos_5.configure(state="normal" if self.pagina_actual > 1 else "disabled")
        self.btn_mas_1.configure(state="normal" if self.pagina_actual < self.total_paginas else "disabled")
        self.btn_mas_5.configure(state="normal" if self.pagina_actual < self.total_paginas else "disabled")

        f_enc = nuevo_frame(self.frame_lista, color_fondo="#1a1a1a")
        f_enc.pack(fill="x", pady=(0, 5), padx=5)
        cols = [2, 3, 2, 2, 2, 3, 2]
        for i, w in enumerate(cols):
            f_enc.grid_columnconfigure(i, weight=w, uniform="vg_turno")

        headers = [
            ("Hora", "w"), ("Referencia", "w"), ("Artículos", "center"),
            ("Total", "e"), ("Estado", "center"), ("Fecha Estado", "center"), ("Acciones", "center")
        ]
        for idx, (t, pos) in enumerate(headers):
            nuevo_label(f_enc, t, fuente=("Arial", 11, "bold"), color_texto="#a0a0a0", poscicion=pos).grid(
                row=0, column=idx, sticky="nsew" if pos == "center" else pos, padx=8, pady=7
            )

        for vg in pagina_items:
            f = nuevo_frame(self.frame_lista, color_fondo="#2b2b2b")
            f.pack(fill="x", pady=3, padx=5)
            for i, w in enumerate(cols):
                f.grid_columnconfigure(i, weight=w, uniform="vg_turno")

            nuevo_label(f, vg["hora"], fuente=("Arial", 11), poscicion="w").grid(row=0, column=0, sticky="w", padx=8, pady=8)
            nuevo_label(f, vg["referencia"], fuente=("Arial", 12, "bold"), color_texto="#4fa6ff", poscicion="w").grid(row=0, column=1, sticky="w", padx=8, pady=8)
            nuevo_label(f, f"{vg['cantidad_articulos']} art.", fuente=("Arial", 11), color_texto="#cccccc", poscicion="center").grid(row=0, column=2, sticky="nsew", pady=8)
            nuevo_label(f, f"${int(vg['total']):,}".replace(",", "."), fuente=("Arial", 11, "bold"), color_texto="#ffffff", poscicion="e").grid(row=0, column=3, sticky="e", padx=8, pady=8)

            estado = vg["estado"]
            if estado == "Pagado":
                txt_est, col_est, col_fecha = "Pagado", COLOR_EXITO, COLOR_EXITO
            elif estado == "Eliminada":
                txt_est, col_est, col_fecha = "Eliminada (Pérdida)", COLOR_FALLO, COLOR_FALLO
            else:
                txt_est, col_est, col_fecha = "Pendiente", "#d4ac0d", "#a0a0a0"

            nuevo_label(f, txt_est, fuente=("Arial", 11, "bold"), color_texto=col_est, poscicion="center").grid(row=0, column=4, sticky="nsew", pady=8)

            nuevo_label(f, vg["texto_pago"], fuente=("Arial", 11, "bold"), color_texto=col_fecha, poscicion="center").grid(row=0, column=5, sticky="nsew", pady=8)

            f_btn = nuevo_frame(f, color_fondo="transparent")
            f_btn.grid(row=0, column=6, sticky="nsew", pady=4)
            nuevo_boton(
                f_btn, "Detalles",
                comando=lambda venta=vg: ModalDetalleVentaIndividual(self.modal, venta, f"Guardada - Ref: {venta['referencia']}"),
                color_fondo="#1f538d", color_hover="#14375e", ancho=80
            ).pack(expand=True)


class ModalVentasTurno:
    """Modal paginado a pantalla completa de las ventas realizadas del turno + botón superior de Ventas Guardadas."""
    def __init__(self, master, caja, ventas, ventas_guardadas):
        self.modal = nuevo_modal(master, f"Ventas del Turno - {caja['encargado']} - {caja['fecha_apertura']}", 1100, 850)
        self.modal.focus_force()
        self.caja = caja
        self.ventas = ventas
        self.ventas_guardadas = ventas_guardadas

        frame_ppal = nuevo_frame(self.modal)
        frame_ppal.pack(expand=True, fill="both", padx=20, pady=15)

        # --- CABECERA SUPERIOR CON TÍTULO Y BOTÓN VENTAS GUARDADAS ---
        frame_top = nuevo_frame(frame_ppal, color_fondo="transparent")
        frame_top.pack(fill="x", pady=(0, 10))

        nuevo_label(
            frame_top,
            f"Ventas Realizadas ({len(ventas)})",
            fuente=("Arial", 16, "bold"),
            color_texto=COLOR_EXITO
        ).pack(side="left")

        nuevo_boton(
            frame_top,
            f"Ventas Guardadas ({len(ventas_guardadas)})",
            comando=lambda: ModalVentasGuardadasTurno(self.modal, self.caja, self.ventas_guardadas),
            color_fondo="#db4e17",
            color_hover="#922F10",
            ancho=190
        ).pack(side="right")

        # --- CONTENEDOR TABLA + PAGINACIÓN ---
        self.frame_contenedor = nuevo_frame(frame_ppal, color_fondo="#202020", radio_esquinas=10)
        self.frame_contenedor.pack(fill="both", expand=True, pady=(0, 10))

        self.frame_lista = nuevo_frame(self.frame_contenedor, color_fondo="transparent")
        self.frame_lista.pack(fill="both", expand=True, padx=10, pady=10)

        self.pagina_actual = 1
        self.items_por_pagina = 7

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

        nuevo_boton(frame_ppal, "Cerrar (Esc)", comando=self.modal.destroy, color_fondo=COLOR_FALLO, color_hover=COLOR_FALLO_HOVER, ancho=140).pack()
        self.modal.bind("<Escape>", lambda e: self.modal.destroy())

    def cambiar_pagina(self, salto):
        nueva = self.pagina_actual + salto
        if nueva < 1:
            nueva = 1
        elif nueva > getattr(self, 'total_paginas', 1):
            nueva = getattr(self, 'total_paginas', 1)

        if nueva != self.pagina_actual:
            self.pagina_actual = nueva
            self.renderizar_pagina()

    def renderizar_pagina(self):
        for w in self.frame_lista.winfo_children():
            w.destroy()

        if not self.ventas:
            nuevo_label(self.frame_lista, "No se registraron ventas cobradas en este turno.", fuente=("Arial", 14, "bold"), color_texto="#a0a0a0").pack(expand=True, pady=80)
            self.frame_paginacion.pack_forget()
            return

        self.frame_paginacion.pack(fill="x", pady=(0, 10))
        self.total_paginas = max(1, (len(self.ventas) + self.items_por_pagina - 1) // self.items_por_pagina)
        if self.pagina_actual > self.total_paginas:
            self.pagina_actual = self.total_paginas

        inicio = (self.pagina_actual - 1) * self.items_por_pagina
        pagina_ventas = self.ventas[inicio:inicio + self.items_por_pagina]

        self.lbl_paginacion.configure(text=f"Página {self.pagina_actual} / {self.total_paginas}")
        self.btn_menos_1.configure(state="normal" if self.pagina_actual > 1 else "disabled")
        self.btn_menos_5.configure(state="normal" if self.pagina_actual > 1 else "disabled")
        self.btn_mas_1.configure(state="normal" if self.pagina_actual < self.total_paginas else "disabled")
        self.btn_mas_5.configure(state="normal" if self.pagina_actual < self.total_paginas else "disabled")

        f_enc = nuevo_frame(self.frame_lista, color_fondo="#1a1a1a")
        f_enc.pack(fill="x", pady=(0, 5), padx=5)
        cols_v = [3, 2, 2, 2, 2]
        for i, w in enumerate(cols_v):
            f_enc.grid_columnconfigure(i, weight=w, uniform="v_turno")

        for idx, (t, pos) in enumerate([("Hora / Origen", "w"), ("Método Pago", "center"), ("Cant. Artículos", "center"), ("Total", "e"), ("Acciones", "center")]):
            nuevo_label(f_enc, t, fuente=("Arial", 12, "bold"), color_texto="#a0a0a0", poscicion=pos).grid(
                row=0, column=idx, sticky="nsew" if pos == "center" else pos, padx=10, pady=7
            )

        for v in pagina_ventas:
            f = nuevo_frame(self.frame_lista, color_fondo="#2b2b2b")
            f.pack(fill="x", pady=3, padx=5)
            for i, w in enumerate(cols_v):
                f.grid_columnconfigure(i, weight=w, uniform="v_turno")

            f_hora = nuevo_frame(f, color_fondo="transparent")
            f_hora.grid(row=0, column=0, sticky="w", padx=10, pady=6)
            nuevo_label(f_hora, v["hora"], fuente=("Arial", 12, "bold"), poscicion="w").pack(anchor="w")
            if v.get("es_guardada_anterior"):
                nuevo_label(
                    f_hora,
                    f"Guardada el {v['fecha_guardada']} (referencia: {v['referencia_guardada']})",
                    fuente=("Arial", 10, "bold"),
                    color_texto="#d4ac0d",
                    poscicion="w"
                ).pack(anchor="w")

            color_met = "#9d64ff" if v["metodo_pago"] == "Nequi" else "#ffffff"
            nuevo_label(f, v["metodo_pago"], fuente=("Arial", 12, "bold"), color_texto=color_met, poscicion="center").grid(row=0, column=1, sticky="nsew", pady=8)
            nuevo_label(f, f"{v['cantidad_articulos']} art.", fuente=("Arial", 12), color_texto="#cccccc", poscicion="center").grid(row=0, column=2, sticky="nsew", pady=8)
            nuevo_label(f, f"${int(v['total']):,}".replace(",", "."), fuente=("Arial", 12, "bold"), color_texto=COLOR_EXITO, poscicion="e").grid(row=0, column=3, sticky="e", padx=10, pady=8)

            f_btn = nuevo_frame(f, color_fondo="transparent")
            f_btn.grid(row=0, column=4, sticky="nsew", pady=4)
            nuevo_boton(
                f_btn, "Detalles",
                comando=lambda venta=v: ModalDetalleVentaIndividual(self.modal, venta),
                color_fondo="#1f538d", color_hover="#14375e", ancho=80
            ).pack(expand=True)


class ModalGastosTurno:
    """Sub-modal con los gastos en efectivo y bajas/pérdidas de inventario del turno."""
    def __init__(self, master, caja, gastos):
        self.modal = nuevo_modal(master, f"Gastos del Turno - {caja['encargado']} - {caja['fecha_apertura']}", 780, 500)
        self.modal.focus_force()

        frame_ppal = nuevo_frame(self.modal)
        frame_ppal.pack(expand=True, fill="both", padx=20, pady=15)

        nuevo_label(frame_ppal, f"Gastos del Turno ({len(gastos)})", fuente=("Arial", 16, "bold"), color_texto="#d4ac0d").pack(pady=(0, 10))

        scroll = ctk.CTkScrollableFrame(frame_ppal, fg_color="#202020")
        scroll.pack(fill="both", expand=True, pady=5)

        if not gastos:
            nuevo_label(scroll, "No se registraron gastos en este turno.", color_texto="#a0a0a0").pack(pady=40)
        else:
            f_enc = nuevo_frame(scroll, color_fondo="#1a1a1a")
            f_enc.pack(fill="x", pady=(0, 5), padx=5)
            cols = [1, 3, 2, 1]
            for i, w in enumerate(cols):
                f_enc.grid_columnconfigure(i, weight=w, uniform="det_g")

            for idx, (t, pos) in enumerate([("Hora", "w"), ("Descripción", "w"), ("Producto / Cant.", "center"), ("Monto / Costo", "e")]):
                nuevo_label(f_enc, t, fuente=("Arial", 12, "bold"), color_texto="#a0a0a0", poscicion=pos).grid(
                    row=0, column=idx, sticky="nsew" if pos == "center" else pos, padx=10, pady=6
                )

            for g in gastos:
                f = nuevo_frame(scroll, color_fondo="#2b2b2b")
                f.pack(fill="x", pady=3, padx=5)
                for i, w in enumerate(cols):
                    f.grid_columnconfigure(i, weight=w, uniform="det_g")

                nuevo_label(f, g["hora"], fuente=("Arial", 11), poscicion="w").grid(row=0, column=0, sticky="w", padx=10, pady=8)

                lbl_desc = nuevo_label(
                    f, g["descripcion"],
                    fuente=("Arial", 12, "bold"),
                    color_texto="#ffffff" if g["tipo"] == "Dinero" else "#d4ac0d",
                    poscicion="w"
                )
                lbl_desc.configure(wraplength=250, justify="left")
                lbl_desc.grid(row=0, column=1, sticky="w", padx=10, pady=8)

                prod_txt = f"{g['producto']} (-{g['cantidad']})" if g["producto"] else "Efectivo"
                nuevo_label(f, prod_txt, fuente=("Arial", 11), color_texto="#a0a0a0", poscicion="center").grid(row=0, column=2, sticky="nsew", pady=8)
                nuevo_label(f, f"${int(g['monto']):,}".replace(",", "."), fuente=("Arial", 12, "bold"), color_texto=COLOR_FALLO, poscicion="e").grid(row=0, column=3, sticky="e", padx=10, pady=8)

        nuevo_boton(frame_ppal, "Cerrar (Esc)", comando=self.modal.destroy, color_fondo=COLOR_FALLO, color_hover=COLOR_FALLO_HOVER, ancho=140).pack(pady=(10, 0))
        self.modal.bind("<Escape>", lambda e: self.modal.destroy())


class ModalDetallesCaja:
    """Mini-clon adaptado del modal de cierre de caja con acceso a ventas y gastos del turno."""
    def __init__(self, master, caja):
        self.modal = nuevo_modal(master, f"Detalles de Caja - {caja['encargado']} - {caja['fecha_apertura']}", 560, 720)
        self.modal.focus_force()

        frame_modal = nuevo_frame(self.modal)
        frame_modal.pack(expand=True, fill="both", padx=20, pady=20)

        nuevo_label(frame_modal, "Resumen del Turno", fuente=FUENTE_TITULOS).pack(pady=(5, 2))
        nuevo_label(
            frame_modal,
            f"Encargado: {caja['encargado']}  |  {caja['fecha_apertura']}",
            fuente=("Arial", 12),
            color_texto="#a0a0a0"
        ).pack(pady=(0, 8))

        resumen = obtener_resumen_caja(caja["id"])
        if not resumen:
            nuevo_label(frame_modal, "Error al cargar el resumen de la caja.", color_texto=COLOR_FALLO).pack(pady=20)
            return

        ventas, ventas_guardadas, gastos = obtener_detalles_turno(caja["id"])

        f_stats = nuevo_frame(frame_modal, color_fondo="#2b2b2b", radio_esquinas=10)
        f_stats.pack(fill="x", pady=8, padx=10)

        self.crear_fila_stat(f_stats, "Ventas Efectivo:", f"${int(resumen['efectivo']):,}".replace(",", "."), COLOR_EXITO)
        self.crear_fila_stat(f_stats, "Ventas Nequi:", f"${int(resumen['nequi']):,}".replace(",", "."), "#9d64ff")

        nuevo_frame(f_stats, color_fondo="#444444", alto=1).pack(fill="x", padx=30, pady=3)

        self.crear_fila_stat(f_stats, "Ganancia Efectivo:", f"${int(resumen['ganancia_efectivo']):,}".replace(",", "."), COLOR_EXITO)
        self.crear_fila_stat(f_stats, "Ganancia Nequi:", f"${int(resumen['ganancia_nequi']):,}".replace(",", "."), "#9d64ff")
        self.crear_fila_stat(f_stats, "Gastos Registrados:", f"- ${int(resumen['gastos']):,}".replace(",", "."), COLOR_FALLO)

        nuevo_frame(f_stats, color_fondo="#444444", alto=2).pack(fill="x", padx=15, pady=5)
        self.crear_fila_stat(f_stats, "Ganancia Neta Total:", f"${int(resumen['ganancia_neta']):,}".replace(",", "."), "#4fa6ff", bold=True)

        f_flujo = nuevo_frame(frame_modal, color_fondo="#1c1c1c", radio_esquinas=10)
        f_flujo.pack(fill="x", pady=8, padx=10)

        nuevo_label(f_flujo, "Cuadre de Caja (Efectivo)", fuente=("Arial", 14, "bold"), color_texto="#d4ac0d").pack(pady=5)
        self.crear_fila_stat(f_flujo, "Base Inicial:", f"${int(resumen['base']):,}".replace(",", "."))
        self.crear_fila_stat(f_flujo, "Entradas (Ventas):", f"+ ${int(resumen['efectivo']):,}".replace(",", "."))
        self.crear_fila_stat(f_flujo, "Salidas (Gastos):", f"- ${int(resumen['gastos']):,}".replace(",", "."))
        self.crear_fila_stat(f_flujo, "Efectivo Esperado en Caja:", f"${int(resumen['efectivo_esperado']):,}".replace(",", "."), "#d4ac0d", bold=True)

        if not resumen["abierta"] and resumen["efectivo_cierre"] is not None:
            nuevo_frame(f_flujo, color_fondo="#444444", alto=1).pack(fill="x", padx=30, pady=4)
            self.crear_fila_stat(f_flujo, "Efectivo Físico Contado:", f"${int(resumen['efectivo_cierre']):,}".replace(",", "."), "#ffffff", bold=True)

            dif = resumen["diferencia"]
            if dif < 0:
                txt_dif, col_dif = f"Faltante: -${int(abs(dif)):,}".replace(",", "."), COLOR_FALLO
            elif dif > 0:
                txt_dif, col_dif = f"Sobrante: +${int(dif):,}".replace(",", "."), COLOR_EXITO
            else:
                txt_dif, col_dif = "$0 (Cuadre Exacto)", COLOR_EXITO
            self.crear_fila_stat(f_flujo, "Diferencia / Cuadre:", txt_dif, col_dif, bold=True)

        if ventas_guardadas:
            pendientes_cnt = sum(1 for vg in ventas_guardadas if vg["estado"] == "Pendiente")
            pagadas_cnt = sum(1 for vg in ventas_guardadas if vg["estado"] == "Pagado")
            eliminadas_cnt = sum(1 for vg in ventas_guardadas if vg["estado"] == "Eliminada")
            nuevo_label(
                frame_modal,
                f"Ventas guardadas del turno: {pagadas_cnt} pagada(s)  |  {pendientes_cnt} pendiente(s)  |  {eliminadas_cnt} eliminada(s)",
                fuente=("Arial", 11, "bold"),
                color_texto="#d4ac0d"
            ).pack(pady=(6, 4))

        frame_acciones = nuevo_frame(frame_modal, color_fondo="transparent")
        frame_acciones.pack(fill="x", padx=10, pady=(12, 6))
        frame_acciones.grid_columnconfigure(0, weight=1)
        frame_acciones.grid_columnconfigure(1, weight=1)

        nuevo_boton(
            frame_acciones,
            f"Ventas del Día ({len(ventas)})",
            comando=lambda: ModalVentasTurno(self.modal, caja, ventas, ventas_guardadas),
            color_fondo="#1f538d",
            color_hover="#14375e"
        ).grid(row=0, column=0, sticky="ew", padx=(0, 6), ipady=4)

        nuevo_boton(
            frame_acciones,
            f"Gastos del Día ({len(gastos)})",
            comando=lambda: ModalGastosTurno(self.modal, caja, gastos),
            color_fondo="#d4ac0d",
            color_hover="#b9770e"
        ).grid(row=0, column=1, sticky="ew", padx=(6, 0), ipady=4)

        nuevo_boton(
            frame_modal,
            "Cerrar (Esc)",
            comando=self.modal.destroy,
            color_fondo=COLOR_FALLO,
            color_hover=COLOR_FALLO_HOVER,
            ancho=160
        ).pack(pady=(10, 0))

        self.modal.bind("<Escape>", lambda e: self.modal.destroy())

    def crear_fila_stat(self, master, label, valor, color="#ffffff", bold=False):
        f = nuevo_frame(master, color_fondo="transparent")
        f.pack(fill="x", padx=15, pady=2)
        fuente_val = ("Arial", 14, "bold") if bold else ("Arial", 14)
        nuevo_label(f, label, fuente=("Arial", 13), color_texto="#a0a0a0", poscicion="w").pack(side="left")
        nuevo_label(f, valor, fuente=fuente_val, color_texto=color, poscicion="e").pack(side="right")