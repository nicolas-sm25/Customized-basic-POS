import customtkinter as ctk
from bll.gestor_caja import obtener_historial_cajas
from ui.componentes.configuracion_componentes import ConfiguracionComponentes
from ui.componentes.creador_componentes import *
from ui.modales.modal_detalles_caja import ModalDetallesCaja
from ui.modales.modal_historial_gastos import ModalHistorialGastos

class VistaHistorial(ConfiguracionComponentes):
    def __init__(self, master):
        super().__init__(master)
        
        # --- CABECERA SUPERIOR ---
        self.frame_top = nuevo_frame(self, color_fondo="transparent")
        self.frame_top.pack(fill="x", padx=20, pady=15)

        self.lbl_titulo = nuevo_label(self.frame_top, "Historial de Cajas y Rendimiento", fuente=FUENTE_TITULOS)
        self.lbl_titulo.pack(side="left")

        self.btn_historial_gastos = nuevo_boton(
            self.frame_top, "Historial de Gastos", 
            comando=self.abrir_historial_gastos, 
            color_fondo="#d4ac0d", color_hover="#b9770e", ancho=180
        )
        self.btn_historial_gastos.pack(side="right")

        self.frame_tabla_container = nuevo_frame(self, color_fondo="#202020", radio_esquinas=10)
        self.frame_tabla_container.pack(fill="both", expand=True, padx=20, pady=10)

        self.scroll_tabla = ctk.CTkScrollableFrame(self.frame_tabla_container, fg_color="transparent")
        self.scroll_tabla.pack(fill="both", expand=True, padx=10, pady=10)

        # --- PAGINACIÓN ---
        self.pagina_actual = 1
        self.items_por_pagina = 13
        
        self.frame_paginacion = nuevo_frame(self.frame_tabla_container, color_fondo="transparent")
        self.frame_paginacion.pack(fill="x", pady=(0, 10))
        
        self.btn_menos_5 = nuevo_boton(self.frame_paginacion, "<< 5 Pags", comando=lambda: self.cambiar_pagina(-5), ancho=90, color_fondo="#1f538d")
        self.btn_menos_5.pack(side="left", padx=(20, 5))
        
        self.btn_menos_1 = nuevo_boton(self.frame_paginacion, "< Anterior", comando=lambda: self.cambiar_pagina(-1), ancho=90, color_fondo="#1f538d")
        self.btn_menos_1.pack(side="left", padx=5)
        
        self.lbl_paginacion = nuevo_label(self.frame_paginacion, "Página 1 / X", fuente=("Arial", 12, "bold"), color_texto="#a0a0a0")
        self.lbl_paginacion.pack(side="left", expand=True)
        
        self.btn_mas_5 = nuevo_boton(self.frame_paginacion, "5 Pags >>", comando=lambda: self.cambiar_pagina(5), ancho=90, color_fondo="#1f538d")
        self.btn_mas_5.pack(side="right", padx=(5, 20))
        
        self.btn_mas_1 = nuevo_boton(self.frame_paginacion, "Siguiente >", comando=lambda: self.cambiar_pagina(1), ancho=90, color_fondo="#1f538d")
        self.btn_mas_1.pack(side="right", padx=5)

        self.cargar_historial()

    def abrir_historial_gastos(self):
        ModalHistorialGastos(self.winfo_toplevel())

    def abrir_detalles_caja(self, caja):
        ModalDetallesCaja(self.winfo_toplevel(), caja)
        
    def cambiar_pagina(self, salto):
        nueva_pagina = self.pagina_actual + salto
        if nueva_pagina < 1: nueva_pagina = 1
        elif nueva_pagina > getattr(self, 'total_paginas', 1): nueva_pagina = getattr(self, 'total_paginas', 1)
            
        if nueva_pagina != self.pagina_actual:
            self.pagina_actual = nueva_pagina
            self.cargar_historial()

    def cargar_historial(self):
        for widget in self.scroll_tabla.winfo_children(): widget.destroy()
        historial = obtener_historial_cajas()

        if not historial:
            nuevo_label(self.scroll_tabla, "No hay historial de cajas registrado.", fuente=("Arial", 16, "bold"), color_texto="#a0a0a0").pack(expand=True, pady=40)
            self.frame_paginacion.pack_forget()
            return
            
        self.frame_paginacion.pack(fill="x", pady=(0, 10))

        # --- PÁGINAS ---
        self.total_paginas = max(1, (len(historial) + self.items_por_pagina - 1) // self.items_por_pagina)
        if self.pagina_actual > self.total_paginas: self.pagina_actual = self.total_paginas
            
        inicio = (self.pagina_actual - 1) * self.items_por_pagina
        fin = inicio + self.items_por_pagina
        historial_pagina = historial[inicio:fin]

        self.lbl_paginacion.configure(text=f"Página {self.pagina_actual} / {self.total_paginas}")
        self.btn_menos_1.configure(state="normal" if self.pagina_actual > 1 else "disabled")
        self.btn_menos_5.configure(state="normal" if self.pagina_actual > 1 else "disabled")
        self.btn_mas_1.configure(state="normal" if self.pagina_actual < self.total_paginas else "disabled")
        self.btn_mas_5.configure(state="normal" if self.pagina_actual < self.total_paginas else "disabled")

        # --- CABECERA DE LA TABLA ---
        f_enc = nuevo_frame(self.scroll_tabla, color_fondo="#1a1a1a")
        f_enc.pack(fill="x", pady=(0, 5), padx=5)

        cols = [2, 2, 2, 2, 2, 2, 2, 2, 2, 2] 
        for i, weight in enumerate(cols):
            f_enc.grid_columnconfigure(i, weight=weight, uniform="hist")
            
        titulos = [
            ("Encargado", "w"), 
            ("Apertura", "center"), 
            ("Cierre", "center"),
            ("Base", "e"), 
            ("Ingresos", "e"), 
            ("Gastos", "e"), 
            ("Utilidad", "e"), 
            ("Cuadre", "e"), 
            ("Físico", "e"),
            ("Acciones", "center")
        ]
        
        for idx, (texto, alinear) in enumerate(titulos):
            anclaje = "nsew" if alinear == "center" else alinear
            nuevo_label(f_enc, texto, fuente=("Arial", 11, "bold"), color_texto="#a0a0a0", poscicion=alinear).grid(row=0, column=idx, sticky=anclaje, padx=5, pady=8)

        # --- FILAS DE DATOS ---
        for caja in historial_pagina:
            f_item = nuevo_frame(self.scroll_tabla, color_fondo="#2b2b2b")
            f_item.pack(fill="x", pady=4, padx=5)
            
            for i, weight in enumerate(cols):
                f_item.grid_columnconfigure(i, weight=weight, uniform="hist")

            # Columna Encargado (con nota si fue recuperada)
            f_enc_celda = nuevo_frame(f_item, color_fondo="transparent")
            f_enc_celda.grid(row=0, column=0, sticky="w", padx=10, pady=8)
            nuevo_label(f_enc_celda, caja['encargado'], fuente=("Arial", 11, "bold"), color_texto="#d4ac0d", poscicion="w").pack(anchor="w")
            if caja.get('recuperada_por'):
                nuevo_label(
                    f_enc_celda,
                    f"🔄 {caja['recuperada_por']}",
                    fuente=("Arial", 9, "italic"),
                    color_texto="#4fa6ff",
                    poscicion="w"
                ).pack(anchor="w")

            nuevo_label(f_item, caja['fecha_apertura'], fuente=("Arial", 11), poscicion="center").grid(row=0, column=1, sticky="nsew", pady=10)
            
            if caja['estado'] == "Abierta":
                color_cierre, peso_cierre = "#d4ac0d", "bold"
            elif caja['estado'] == "Incompleta":
                color_cierre, peso_cierre = "#db4e17", "bold"
            else:
                color_cierre, peso_cierre = "#ffffff", "normal"

            nuevo_label(f_item, caja['fecha_cierre'], fuente=("Arial", 11, peso_cierre), color_texto=color_cierre, poscicion="center").grid(row=0, column=2, sticky="nsew", pady=10)
            
            nuevo_label(f_item, f"${int(caja['base']):,}".replace(",", "."), fuente=("Arial", 11), poscicion="e").grid(row=0, column=3, sticky="e", pady=10, padx=5)
            nuevo_label(f_item, f"${int(caja['ventas']):,}".replace(",", "."), fuente=("Arial", 11, "bold"), color_texto=COLOR_EXITO, poscicion="e").grid(row=0, column=4, sticky="e", pady=10, padx=5)
            nuevo_label(f_item, f"${int(caja['gastos']):,}".replace(",", "."), fuente=("Arial", 11, "bold"), color_texto=COLOR_FALLO, poscicion="e").grid(row=0, column=5, sticky="e", pady=10, padx=5)
            nuevo_label(f_item, f"${int(caja['ganancia_neta']):,}".replace(",", "."), fuente=("Arial", 11, "bold"), color_texto="#4fa6ff", poscicion="e").grid(row=0, column=6, sticky="e", pady=10, padx=5)
            
            dif = caja['diferencia']
            col_dif = COLOR_EXITO if dif >= 0 else COLOR_FALLO
            txt_dif = f"+${int(dif):,}".replace(",", ".") if dif >= 0 else f"-${abs(int(dif)):,}".replace(",", ".")
            if caja['estado'] != "Cerrada":
                txt_dif, col_dif = "-", "#a0a0a0"
                
            nuevo_label(f_item, txt_dif, fuente=("Arial", 11, "bold"), color_texto=col_dif, poscicion="e").grid(row=0, column=7, sticky="e", pady=10, padx=5)
            
            efectivo_fisico_real = (caja['base'] + caja['ventas'] - caja['gastos'] + caja['diferencia']) if caja['estado'] == "Cerrada" else 0
            if caja['estado'] == "Cerrada":
                txt_efectivo, col_ef = f"${int(efectivo_fisico_real):,}".replace(",", "."), "#ffffff"
            elif caja['estado'] == "Incompleta":
                txt_efectivo, col_ef = "Sin cierre", "#db4e17"
            else:
                txt_efectivo, col_ef = "En curso...", "#d4ac0d"

            nuevo_label(f_item, txt_efectivo, fuente=("Arial", 11, "bold"), color_texto=col_ef, poscicion="e").grid(row=0, column=8, sticky="e", pady=10, padx=5)

            f_btn = nuevo_frame(f_item, color_fondo="transparent")
            f_btn.grid(row=0, column=9, sticky="nsew", padx=5, pady=5)
            if caja['estado'] == "Cerrada":
                nuevo_boton(f_btn, "Detalles", comando=lambda c=caja: self.abrir_detalles_caja(c), color_fondo="#1f538d", color_hover="#14375e", ancho=75).pack(expand=True)
            elif caja['estado'] == "Incompleta":
                nuevo_boton(f_btn, "Auditar", comando=lambda c=caja: self.auditar_caja_incompleta(c), color_fondo="#db4e17", color_hover="#922F10", ancho=75).pack(expand=True)
            else:
                nuevo_label(f_btn, "-", color_texto="#a0a0a0", poscicion="center").pack(expand=True)
                
    def auditar_caja_incompleta(self, caja):
            from ui.modales.modal_cierre_caja import ModalCierreCaja
            from bll.gestor_caja import cerrar_caja_definitiva

            def confirmar_auditoria(efectivo_fisico, diferencia):
                admin = getattr(self.winfo_toplevel(), 'usuario_actual', {}).get('nombre', 'Administrador')
                exito, _ = cerrar_caja_definitiva(caja['id'], efectivo_fisico, diferencia, auditada_por=admin)
                if exito:
                    self.cargar_historial()

            ModalCierreCaja(self.winfo_toplevel(), caja['id'], confirmar_auditoria)

    def abrir_guardadas_de_turno(self, caja, venta_resaltada_id=None):
        from bll.gestor_caja import obtener_detalles_turno
        from ui.modales.modal_detalles_caja import ModalVentasGuardadasTurno

        _, ventas_guardadas, _ = obtener_detalles_turno(caja["id"])
        ModalVentasGuardadasTurno(
            self.winfo_toplevel(),
            caja,
            ventas_guardadas,
            venta_resaltada_id=venta_resaltada_id
        )