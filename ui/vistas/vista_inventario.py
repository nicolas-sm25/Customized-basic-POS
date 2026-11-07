import customtkinter as ctk
from bll.gestor_productos import obtener_inventario_completo, desactivar_producto_db, reactivar_producto_db
from bll.gestor_ventas import obtener_ventas_pendientes
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

        productos_totales = obtener_inventario_completo()
        productos_activos = [p for p in productos_totales if p['activo']]
        self.productos_inactivos = [p for p in productos_totales if not p['activo']]
        
        ventas_pendientes = obtener_ventas_pendientes()

        cant_activos = len(productos_activos)
        cant_inactivos = len(self.productos_inactivos)
        cant_pendientes = len(ventas_pendientes)

        for w in self.frame_top.winfo_children(): w.destroy()
        
        self.lbl_mensaje = nuevo_label(self.frame_top, "", color_texto=COLOR_EXITO)
        self.lbl_mensaje.pack(side="left")

        nuevo_label(self.frame_top, f"Cantidad de productos: {cant_activos}", fuente=("Arial", 13, "bold"), color_texto="#a0a0a0").pack(side="left", padx=20)
        
        btn_ver_guardadas = nuevo_boton(self.frame_top, f"Ver Pedidos Guardados ({cant_pendientes})", comando=self.abrir_pedidos_solo_lectura, color_fondo="#d4ac0d", color_hover="#b9770e", ancho=210)
        btn_ver_guardadas.pack(side="right", padx=5)

        self.btn_ver_inactivos = nuevo_boton(self.frame_top, f"Ver Inhabilitados ({cant_inactivos})", comando=self.abrir_modal_inactivos, color_fondo="#db4e17", color_hover="#922F10", ancho=180)
        self.btn_ver_inactivos.pack(side="right", padx=5)

        if not productos_activos:
            for widget in self.scroll_tabla.winfo_children(): widget.destroy()
            lbl_vacio = nuevo_label(self.scroll_tabla, "No hay productos activos en el inventario.", fuente=("Arial", 16, "bold"), color_texto="#a0a0a0")
            lbl_vacio.pack(expand=True, pady=40)
            return

        if hasattr(self, 'lbl_alerta_stock'):
            self.lbl_alerta_stock.destroy()

        for widget in self.scroll_tabla.winfo_children(): widget.destroy()

        # --- CABECERA DE LA TABLA ---
        f_enc = nuevo_frame(self.scroll_tabla, color_fondo="#1a1a1a")
        f_enc.pack(fill="x", pady=(0, 5), padx=5)

        cols = [4, 2, 2, 2, 2]
        for i, w in enumerate(cols): f_enc.grid_columnconfigure(i, weight=w, uniform="inv")

        titulos = [("Producto", "w"), ("Costo", "e"), ("Precio Venta", "e"), ("Stock", "center"), ("Acciones", "center")]
        for idx, (t, a) in enumerate(titulos):
            anclaje = "nsew" if a == "center" else a
            nuevo_label(f_enc, t, fuente=("Arial", 14, "bold"), color_texto="#a0a0a0", poscicion=a).grid(row=0, column=idx, sticky=anclaje, padx=10 if a=="w" else 0, pady=8)

        # --- FILAS DE PRODUCTOS (SOLO ACTIVOS) ---
        for prod in productos_activos:
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

            nuevo_label(f_item, f"${int(prod['costo']):,}".replace(",", "."), fuente=("Arial", 16), color_texto="#cccccc").grid(row=0, column=1, sticky="e", pady=10)
            nuevo_label(f_item, f"${int(prod['precio_venta']):,}".replace(",", "."), fuente=("Arial", 16, "bold"), color_texto=COLOR_EXITO).grid(row=0, column=2, sticky="e", pady=10)
            
            color_stock = COLOR_FALLO if prod['stock'] <= 0 else "#ffffff"
            texto_stock = f"{prod['stock']} ⚠️" if prod['stock'] <= 0 else str(prod['stock'])
            nuevo_label(f_item, texto_stock, fuente=("Arial", 16, "bold"), color_texto=color_stock, poscicion="center").grid(row=0, column=3, sticky="nsew", pady=10)
            
            # Botones de Acción
            frame_btn = nuevo_frame(f_item, color_fondo="transparent")
            frame_btn.grid(row=0, column=4, sticky="nsew", padx=5, pady=5)
            
            criterio_busqueda = prod.get('codigo_barras') if prod.get('codigo_barras') else prod.get('nombre', '')
            nuevo_boton(frame_btn, "Editar", comando=lambda c=criterio_busqueda: self.winfo_toplevel().mostrar_editar(c), color_fondo="#3498db", color_hover="#2980b9", ancho=65).pack(side="left", padx=5, expand=True)

            nuevo_boton(frame_btn, "Deshabilitar", comando=lambda id=prod['id'], n=prod['nombre']: self.confirmar_cambio_estado(id, n, False), color_fondo="#961605", color_hover="#631106", ancho=90).pack(side="right", padx=5, expand=True)

        # --- ALERTA DE STOCK NEGATIVO ---
        if any(p['stock'] < 0 for p in productos_activos):
            self.lbl_alerta_stock = nuevo_label(self.frame_tabla_container, "⚠️ ¡ALERTA! Existen productos con stock en negativo. Se requiere registrar reabastecimiento urgente.", color_texto=COLOR_FALLO, fuente=("Arial", 13, "bold"))
            self.lbl_alerta_stock.pack(pady=5)

    def abrir_modal_inactivos(self):
        ModalProductosInactivos(
            self.winfo_toplevel(), 
            self.productos_inactivos, 
            lambda p_id: self.ejecutar_cambio_estado(p_id, True)
        )

    def abrir_pedidos_solo_lectura(self):
        from ui.modales.modal_ventas_guardadas import ModalVentasGuardadas
        from bll.gestor_ventas import obtener_ventas_pendientes
        
        ventas_pendientes = obtener_ventas_pendientes()
        ModalVentasGuardadas(self, ventas_pendientes, callback_recuperar=None, callback_eliminar=None)

    def confirmar_cambio_estado(self, producto_id, nombre_producto, es_activacion):
        ModalConfirmacionEstado(self, nombre_producto, es_activacion, lambda: self.ejecutar_cambio_estado(producto_id, es_activacion))

    def ejecutar_cambio_estado(self, producto_id, es_activacion):
        exito, mensaje = reactivar_producto_db(producto_id) if es_activacion else desactivar_producto_db(producto_id)
        self.lbl_mensaje.configure(text=mensaje, text_color=COLOR_EXITO if exito else COLOR_FALLO)
        if exito: self.cargar_inventario()