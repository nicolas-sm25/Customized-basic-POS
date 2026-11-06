import customtkinter as ctk
from bll.gestor_productos import obtener_inventario_completo, desactivar_producto_db, reactivar_producto_db
from ui.componentes.configuracion_componentes import ConfiguracionComponentes
from ui.componentes.creador_componentes import *
from ui.modales.modal_inventario import ModalConfirmacionEstado
from ui.modales.modal_productos_inactivos import ModalProductosInactivos

class VistaInventario(ConfiguracionComponentes):
    def __init__(self, master):
        super().__init__(master)
        
        # --- TÍTULO ---
        self.lbl_titulo = nuevo_label(self, "Inventario General de Productos", fuente=FUENTE_TITULOS)
        self.lbl_titulo.pack(pady=15)

        # --- PANEL SUPERIOR ---
        self.frame_top = nuevo_frame(self, color_fondo="transparent")
        self.frame_top.pack(fill="x", padx=20, pady=5)

        self.lbl_mensaje = nuevo_label(self.frame_top, "", color_texto=COLOR_EXITO)
        self.lbl_mensaje.pack(side="left")

        self.btn_ver_inactivos = nuevo_boton(self.frame_top, "Ver Inhabilitados (0)", comando=self.abrir_modal_inactivos, color_fondo="#db4e17", color_hover="#922F10", ancho=180)
        self.btn_ver_inactivos.pack(side="right")

        # --- CONTENEDOR DE LA TABLA ---
        self.frame_tabla_container = nuevo_frame(self, color_fondo="#202020", radio_esquinas=10)
        self.frame_tabla_container.pack(fill="both", expand=True, padx=20, pady=10)

        self.scroll_tabla = ctk.CTkScrollableFrame(self.frame_tabla_container, fg_color="transparent")
        self.scroll_tabla.pack(fill="both", expand=True, padx=10, pady=10)

        self.cargar_inventario()

    def cargar_inventario(self):
        """Consulta el BLL, separa los inactivos y dibuja la tabla SOLO con productos activos."""
        for widget in self.scroll_tabla.winfo_children():
            widget.destroy()

        productos_totales = obtener_inventario_completo()
        
        productos_activos = [p for p in productos_totales if p['activo']]
        self.productos_inactivos = [p for p in productos_totales if not p['activo']]

        self.btn_ver_inactivos.configure(text=f"Ver Inhabilitados ({len(self.productos_inactivos)})")

        if not productos_activos:
            lbl_vacio = nuevo_label(self.scroll_tabla, "No hay productos activos en el inventario.", fuente=("Arial", 16, "bold"), color_texto="#a0a0a0")
            lbl_vacio.pack(expand=True, pady=40)
            return

        if hasattr(self, 'lbl_alerta_stock'):
            self.lbl_alerta_stock.destroy()

        # --- CABECERA DE LA TABLA ---
        f_enc = nuevo_frame(self.scroll_tabla, color_fondo="#1a1a1a")
        f_enc.pack(fill="x", pady=(0, 5), padx=5)
        
        cols = [3, 2, 2, 2, 3, 2]
        for i, w in enumerate(cols): f_enc.grid_columnconfigure(i, weight=w, uniform="inv")
        
        titulos = [("Producto", "w"), ("Costo", "e"), ("Precio Venta", "e"), ("Stock", "center"), ("Paquete de", "center"), ("Acciones", "center")]
        for idx, (t, a) in enumerate(titulos):
            anclaje = "nsew" if a == "center" else a
            nuevo_label(f_enc, t, fuente=("Arial", 14, "bold"), color_texto="#a0a0a0", poscicion=a).grid(row=0, column=idx, sticky=anclaje, padx=10 if a=="w" else 0, pady=8)

        # --- FILAS DE PRODUCTOS (SOLO ACTIVOS) ---
        for prod in productos_activos:
            f_item = nuevo_frame(self.scroll_tabla, color_fondo="#2b2b2b")
            f_item.pack(fill="x", pady=4, padx=5)
            
            for i, w in enumerate(cols): f_item.grid_columnconfigure(i, weight=w, uniform="inv")

            nuevo_label(f_item, prod['nombre'], fuente=("Arial", 14, "bold"), color_texto="#4fa6ff", poscicion="w").grid(row=0, column=0, sticky="w", padx=10, pady=10)
            
            nuevo_label(f_item, f"${int(prod['costo']):,}".replace(",", "."), fuente=("Arial", 13), color_texto="#cccccc").grid(row=0, column=1, sticky="e", pady=10)
            nuevo_label(f_item, f"${int(prod['precio_venta']):,}".replace(",", "."), fuente=("Arial", 13, "bold"), color_texto=COLOR_EXITO).grid(row=0, column=2, sticky="e", pady=10)
            
            color_stock = COLOR_FALLO if prod['stock'] <= 0 else "#ffffff"
            texto_stock = f"{prod['stock']} ⚠️" if prod['stock'] <= 0 else str(prod['stock'])
            nuevo_label(f_item, texto_stock, fuente=("Arial", 14, "bold"), color_texto=color_stock, poscicion="center").grid(row=0, column=3, sticky="nsew", pady=10)
            
            texto_paq = f"{prod['info_paquete']} ⚠️ (Unidad Inactiva)" if prod['unidad_inactiva'] else prod['info_paquete']
            color_paq = COLOR_FALLO if prod['unidad_inactiva'] else ("#d4ac0d" if prod['es_paquete'] else "#666666")
            nuevo_label(f_item, texto_paq, fuente=("Arial", 11, "bold"), color_texto=color_paq, poscicion="center").grid(row=0, column=4, sticky="nsew", pady=10)
            
            # Botones de Acción (Editar y Deshabilitar)
            frame_btn = nuevo_frame(f_item, color_fondo="transparent")
            frame_btn.grid(row=0, column=5, sticky="nsew", padx=5, pady=5)
            
            criterio_busqueda = prod.get('codigo_barras') if prod.get('codigo_barras') else prod.get('nombre', '')
            nuevo_boton(frame_btn, "Editar", comando=lambda c=criterio_busqueda: self.winfo_toplevel().mostrar_editar(c), color_fondo="#3498db", color_hover="#2980b9", ancho=65).pack(side="left", padx=2, expand=True)

            nuevo_boton(frame_btn, "X", comando=lambda id=prod['id'], n=prod['nombre']: self.confirmar_cambio_estado(id, n, False), color_fondo=COLOR_FALLO, color_hover=COLOR_FALLO_HOVER, ancho=35).pack(side="right", padx=2, expand=True)

        # --- ALERTA DE STOCK NEGATIVO (Aplica solo a activos) ---
        if any(p['stock'] < 0 for p in productos_activos):
            self.lbl_alerta_stock = nuevo_label(self.frame_tabla_container, "⚠️ ¡ALERTA! Existen productos con stock en negativo. Se requiere registrar reabastecimiento urgente.", color_texto=COLOR_FALLO, fuente=("Arial", 13, "bold"))
            self.lbl_alerta_stock.pack(pady=5)

    def abrir_modal_inactivos(self):
        from ui.modales.modal_productos_inactivos import ModalProductosInactivos
        ModalProductosInactivos(
            self.winfo_toplevel(), 
            self.productos_inactivos, 
            lambda p_id: self.ejecutar_cambio_estado(p_id, True)
        )

    def confirmar_cambio_estado(self, producto_id, nombre_producto, es_activacion):
        ModalConfirmacionEstado(self, nombre_producto, es_activacion, lambda: self.ejecutar_cambio_estado(producto_id, es_activacion))

    def ejecutar_cambio_estado(self, producto_id, es_activacion):
        exito, mensaje = reactivar_producto_db(producto_id) if es_activacion else desactivar_producto_db(producto_id)
        self.lbl_mensaje.configure(text=mensaje, text_color=COLOR_EXITO if exito else COLOR_FALLO)
        if exito: self.cargar_inventario()