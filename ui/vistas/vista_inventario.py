import customtkinter as ctk
from bll.gestor_productos import obtener_inventario_completo, desactivar_producto_db, reactivar_producto_db
from bll.gestor_ventas import obtener_ventas_pendientes
from ui.vistas.secciones.panel_autocompletado import PanelAutocompletado
from ui.componentes.configuracion_componentes import ConfiguracionComponentes
from ui.componentes.creador_componentes import *
from ui.modales.modal_inventario import ModalConfirmacionEstado
from ui.modales.modal_productos_inactivos import ModalProductosInactivos

class VistaInventario(ConfiguracionComponentes):
    def __init__(self, master):
        super().__init__(master)

        self.lbl_titulo = nuevo_label(self, "Inventario General de Productos", fuente=FUENTE_TITULOS)
        self.lbl_titulo.pack(pady=15)

        # --- CONTENEDOR SUPERIOR ---
        self.frame_top = nuevo_frame(self, color_fondo="transparent")
        self.frame_top.pack(fill="x", padx=20, pady=5)
        
        # Bloque Búsqueda
        self.frame_busqueda = nuevo_frame(self.frame_top, color_fondo="transparent")
        self.frame_busqueda.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.entry_busqueda = nueva_caja_texto(self.frame_busqueda, placeholder="Buscar en inventario (Cod/Nombre)...")
        self.entry_busqueda.pack(side="left", fill="x", expand=True)
        self.entry_busqueda.bind("<Return>", self.ejecutar_busqueda)
        
        self.btn_buscar_reset = nuevo_boton(self.frame_busqueda, "Buscar", comando=self.ejecutar_busqueda, ancho=80, color_fondo="#1f538d", color_hover="#14375e")
        self.btn_buscar_reset.pack(side="left", padx=5)

        self.frame_info = nuevo_frame(self.frame_top, color_fondo="transparent")
        self.frame_info.pack(side="left", padx=10)
        self.lbl_cantidad = nuevo_label(self.frame_info, "", fuente=("Arial", 13, "bold"), color_texto="#a0a0a0")
        self.lbl_cantidad.pack()

        # Botones 
        self.btn_ver_inactivos = nuevo_boton(self.frame_top, "Ver Inhabilitados (0)", comando=self.abrir_modal_inactivos, color_fondo="#db4e17", color_hover="#922F10", ancho=180)
        self.btn_ver_inactivos.pack(side="right")
        
        self.btn_ver_guardadas = nuevo_boton(self.frame_top, "Ver Pedidos Guardados", comando=self.abrir_pedidos_solo_lectura, color_fondo="#d4ac0d", color_hover="#b9770e", ancho=210)
        self.btn_ver_guardadas.pack(side="right", padx=5)

        # --- CONTENEDOR TABLA ---
        self.frame_tabla_container = nuevo_frame(self, color_fondo="#202020", radio_esquinas=10)
        self.frame_tabla_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # --- AUTOCOMPLETADO ---
        self.scroll_tabla = ctk.CTkScrollableFrame(self.frame_tabla_container, fg_color="transparent")
        self.autocompletado = PanelAutocompletado(self.entry_busqueda, self.frame_tabla_container, self.scroll_tabla, self.resultado_autocompletado)
        self.scroll_tabla.pack(fill="both", expand=True, padx=10, pady=10)

        # --- PAGINACIÓN ---
        self.pagina_actual = 1
        self.items_por_pagina = 12
        
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

        self.filtro_actual = None
        self.cargar_inventario()

    # --- LÓGICA DE BÚSQUEDA Y AUTOCOMPLETADO ---
    def resultado_autocompletado(self, producto):
        self.entry_busqueda.delete(0, 'end')
        self.entry_busqueda.insert(0, producto['nombre'])
        self.ejecutar_busqueda(None)

    def ejecutar_busqueda(self, event=None):
        if self.autocompletado.procesar_enter(): return "break"
        
        criterio = self.entry_busqueda.get().strip().lower().replace(" ", "")

        if (event is None and self.btn_buscar_reset.cget("text") == "Quitar Filtro") or not criterio:
            self.entry_busqueda.delete(0, 'end')
            self.filtro_actual = None
            self.btn_buscar_reset.configure(text="Buscar", fg_color="#1f538d", hover_color="#14375e")
            self.pagina_actual = 1
            self.cargar_inventario()
            self.after(5, self.entry_busqueda.focus())
            return

        todos_los_productos = obtener_inventario_completo()
        self.filtro_actual = []
        
        for p in todos_los_productos:
            cod = str(p.get('codigo_barras', '')).lower()
            nom = p['nombre'].lower().replace(" ", "")
            if criterio in cod or criterio in nom:
                self.filtro_actual.append(p)
                
        self.btn_buscar_reset.configure(text="Quitar Filtro", fg_color="#961605", hover_color="#631106")
        self.pagina_actual = 1
        self.cargar_inventario()

    def cambiar_pagina(self, salto):
        nueva_pagina = self.pagina_actual + salto
        if nueva_pagina < 1: nueva_pagina = 1
        elif nueva_pagina > getattr(self, 'total_paginas', 1): nueva_pagina = getattr(self, 'total_paginas', 1)
            
        if nueva_pagina != self.pagina_actual:
            self.pagina_actual = nueva_pagina
            self.cargar_inventario()

    # --- RENDERIZADO DEL INVENTARIO ---
    def cargar_inventario(self):
        for widget in self.scroll_tabla.winfo_children(): 
            widget.destroy()

        if self.filtro_actual is not None:
            productos_totales = self.filtro_actual
        else:
            productos_totales = obtener_inventario_completo()

        productos_activos = [p for p in productos_totales if p['activo']]
        self.productos_inactivos = [p for p in productos_totales if not p['activo']]

        self.lbl_cantidad.configure(text=f"Cantidad de productos: {len(productos_activos)}")
        self.btn_ver_inactivos.configure(text=f"Ver Inhabilitados ({len(self.productos_inactivos)})")
        self.btn_ver_guardadas.configure(text=f"Ver Pedidos Guardados ({len(obtener_ventas_pendientes())})")

        if not productos_activos:
            nuevo_label(self.scroll_tabla, "No se encontraron productos.", fuente=("Arial", 16, "bold"), color_texto="#a0a0a0").pack(expand=True, pady=40)
            self.frame_paginacion.pack_forget()
            return

        if hasattr(self, 'lbl_alerta_stock'): self.lbl_alerta_stock.destroy()
        self.frame_paginacion.pack(fill="x", pady=(0, 10))

        # --- PAGINACIÓN ---
        self.total_paginas = max(1, (len(productos_activos) + self.items_por_pagina - 1) // self.items_por_pagina)
        if self.pagina_actual > self.total_paginas: self.pagina_actual = self.total_paginas
            
        inicio = (self.pagina_actual - 1) * self.items_por_pagina
        fin = inicio + self.items_por_pagina
        productos_pagina = productos_activos[inicio:fin]

        self.lbl_paginacion.configure(text=f"Página {self.pagina_actual} / {self.total_paginas}")
        self.btn_menos_1.configure(state="normal" if self.pagina_actual > 1 else "disabled")
        self.btn_menos_5.configure(state="normal" if self.pagina_actual > 1 else "disabled")
        self.btn_mas_1.configure(state="normal" if self.pagina_actual < self.total_paginas else "disabled")
        self.btn_mas_5.configure(state="normal" if self.pagina_actual < self.total_paginas else "disabled")

        # --- CABECERA DE LA TABLA ---
        f_enc = nuevo_frame(self.scroll_tabla, color_fondo="#1a1a1a")
        f_enc.pack(fill="x", pady=(0, 5), padx=5)

        cols = [4, 2, 2, 2, 2]
        for i, w in enumerate(cols): f_enc.grid_columnconfigure(i, weight=w, uniform="inv")

        titulos = [("Producto", "w"), ("Costo", "e"), ("Precio Venta", "e"), ("Stock", "center"), ("Acciones", "center")]
        for idx, (t, a) in enumerate(titulos):
            anclaje = "nsew" if a == "center" else a
            nuevo_label(f_enc, t, fuente=("Arial", 14, "bold"), color_texto="#a0a0a0", poscicion=a).grid(row=0, column=idx, sticky=anclaje, padx=10 if a=="w" else 0, pady=8)

        # --- FILAS DE PRODUCTOS ---
        for prod in productos_pagina:
            f_item = nuevo_frame(self.scroll_tabla, color_fondo="#2b2b2b")
            f_item.pack(fill="x", pady=4, padx=5)
            
            for i, w in enumerate(cols): f_item.grid_columnconfigure(i, weight=w, uniform="inv")

            f_nombre_paq = nuevo_frame(f_item, color_fondo="transparent")
            f_nombre_paq.grid(row=0, column=0, sticky="w", padx=10, pady=10)
            
            nuevo_label(f_nombre_paq, prod['nombre'], fuente=("Arial", 18, "bold"), color_texto="#4fa6ff", poscicion="w").pack(side="left")
            
            if prod['es_paquete']:
                texto_paq = f" (Paq. de: {prod['info_paquete']})"
                if prod['unidad_inactiva']: texto_paq += " ⚠️ Base Inactiva"
                color_paq = COLOR_FALLO if prod['unidad_inactiva'] else "#888888"
                nuevo_label(f_nombre_paq, texto_paq, fuente=("Arial", 11, "italic"), color_texto=color_paq, poscicion="w").pack(side="left", padx=(5,0), pady=(3,0))

            color_costo = "#d4ac0d" if prod['costo'] == 0 else "#cccccc"
            nuevo_label(f_item, f"${int(prod['costo']):,}".replace(",", "."), fuente=("Arial", 16, "bold" if prod['costo'] == 0 else "normal"), color_texto=color_costo).grid(row=0, column=1, sticky="e", pady=10)
            nuevo_label(f_item, f"${int(prod['precio_venta']):,}".replace(",", "."), fuente=("Arial", 16, "bold"), color_texto=COLOR_EXITO).grid(row=0, column=2, sticky="e", pady=10)
            
            color_stock = COLOR_FALLO if prod['stock'] <= 0 else "#ffffff"
            texto_stock = f"{prod['stock']} ⚠️" if prod['stock'] <= 0 else str(prod['stock'])
            nuevo_label(f_item, texto_stock, fuente=("Arial", 16, "bold"), color_texto=color_stock, poscicion="center").grid(row=0, column=3, sticky="nsew", pady=10)
            
            frame_btn = nuevo_frame(f_item, color_fondo="transparent")
            frame_btn.grid(row=0, column=4, sticky="nsew", padx=5, pady=5)
            
            criterio_busqueda = prod.get('codigo_barras') if prod.get('codigo_barras') else prod.get('nombre', '')
            nuevo_boton(frame_btn, "Editar", comando=lambda c=criterio_busqueda: self.winfo_toplevel().mostrar_editar(c), color_fondo="#3498db", color_hover="#2980b9", ancho=65).pack(side="left", padx=5, expand=True)

        # --- ALERTA DE STOCK NEGATIVO Y COSTO CERO ---
        alertas = []
        if any(p['stock'] < 0 for p in productos_activos):
            alertas.append("⚠️ Existen productos con stock en negativo.")
            
        if any(p['costo'] == 0 for p in productos_activos):
            alertas.append("⚠️ Existen productos con costo $0 (Revisar si es correcto).")
            
        if alertas:

            texto_alerta = " | ".join(alertas)

            if "⚠️ Existen productos con stock en negativo." in alertas: 
                color_texto_parcial = COLOR_FALLO 
            else: 
                color_texto_parcial = "#d4ac0d"

            self.lbl_alerta_stock = nuevo_label(self.frame_tabla_container, texto_alerta, color_texto=color_texto_parcial, fuente=("Arial", 13, "bold"))
            self.lbl_alerta_stock.pack(pady=5)

    # --- POP-UPS ---
    def abrir_modal_inactivos(self):
        ModalProductosInactivos(self.winfo_toplevel(), self.productos_inactivos, lambda p_id: self.ejecutar_cambio_estado(p_id, True))

    def abrir_pedidos_solo_lectura(self):
        from ui.modales.modal_ventas_guardadas import ModalVentasGuardadas
        ventas_pendientes = obtener_ventas_pendientes()
        ModalVentasGuardadas(self, ventas_pendientes, callback_recuperar=None, callback_eliminar=None)

    def confirmar_cambio_estado(self, producto_id, nombre_producto, es_activacion):
        ModalConfirmacionEstado(self, nombre_producto, es_activacion, lambda: self.ejecutar_cambio_estado(producto_id, es_activacion))

    def ejecutar_cambio_estado(self, producto_id, es_activacion):
        exito, mensaje = reactivar_producto_db(producto_id) if es_activacion else desactivar_producto_db(producto_id)
        if exito: self.cargar_inventario()