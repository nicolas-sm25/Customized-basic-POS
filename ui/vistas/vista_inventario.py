import customtkinter as ctk
from bll.gestor_productos import obtener_inventario_completo, desactivar_producto_db, reactivar_producto_db
from ui.componentes.configuracion_componentes import ConfiguracionComponentes
from ui.componentes.creador_componentes import *
from ui.modales.modal_inventario import ModalConfirmacionEstado

class VistaInventario(ConfiguracionComponentes):
    def __init__(self, master):
        super().__init__(master)
        
        # --- TÍTULO ---
        self.lbl_titulo = nuevo_label(self, "Inventario General de Productos", fuente=FUENTE_TITULOS)
        self.lbl_titulo.pack(pady=15)

        # --- MENSAJE DE ESTADO ---
        self.lbl_mensaje = nuevo_label(self, "", color_texto=COLOR_EXITO)
        self.lbl_mensaje.pack(pady=5)

        # --- CONTENEDOR DE LA TABLA ---
        self.frame_tabla_container = nuevo_frame(self, color_fondo="#202020", radio_esquinas=10)
        self.frame_tabla_container.pack(fill="both", expand=True, padx=20, pady=10)

        self.scroll_tabla = ctk.CTkScrollableFrame(self.frame_tabla_container, fg_color="transparent")
        self.scroll_tabla.pack(fill="both", expand=True, padx=10, pady=10)

        self.cargar_inventario()

    def cargar_inventario(self):
        """Consulta el BLL y dibuja la tabla de productos."""
        for widget in self.scroll_tabla.winfo_children():
            widget.destroy()

        productos = obtener_inventario_completo()

        if not productos:
            lbl_vacio = nuevo_label(self.scroll_tabla, "No hay productos registrados en la base de datos.", fuente=("Arial", 16, "bold"), color_texto="#a0a0a0")
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

        # --- FILAS DE PRODUCTOS ---
        for prod in productos:
            color_fondo_fila = "#2b2b2b" if prod['activo'] else "#1c1c1c"
            f_item = nuevo_frame(self.scroll_tabla, color_fondo=color_fondo_fila)
            f_item.pack(fill="x", pady=4, padx=5)
            
            for i, w in enumerate(cols): f_item.grid_columnconfigure(i, weight=w, uniform="inv")

            nombre_mostrar = prod['nombre'] if prod['activo'] else f"{prod['nombre']} (Inactivo)"
            color_nombre = "#4fa6ff" if prod['activo'] else "#666666"
            nuevo_label(f_item, nombre_mostrar, fuente=("Arial", 14, "bold" if prod['activo'] else "normal"), color_texto=color_nombre, poscicion="w").grid(row=0, column=0, sticky="w", padx=10, pady=10)
            
            nuevo_label(f_item, f"${int(prod['costo']):,}".replace(",", "."), fuente=("Arial", 13), color_texto="#888888" if not prod['activo'] else "#cccccc").grid(row=0, column=1, sticky="e", pady=10)
            nuevo_label(f_item, f"${int(prod['precio_venta']):,}".replace(",", "."), fuente=("Arial", 13, "bold"), color_texto="#448844" if not prod['activo'] else COLOR_EXITO).grid(row=0, column=2, sticky="e", pady=10)
            
            color_stock = COLOR_FALLO if prod['stock'] <= 5 else ("#ffffff" if prod['activo'] else "#888888")
            texto_stock = f"{prod['stock']} ⚠️" if prod['stock'] <= 5 else str(prod['stock'])
            nuevo_label(f_item, texto_stock, fuente=("Arial", 14, "bold"), color_texto=color_stock, poscicion="center").grid(row=0, column=3, sticky="nsew", pady=10)
            
            texto_paq = f"{prod['info_paquete']} ⚠️ (Unidad Inactiva)" if prod['unidad_inactiva'] else prod['info_paquete']
            color_paq = COLOR_FALLO if prod['unidad_inactiva'] else ("#d4ac0d" if prod['es_paquete'] else "#666666")
            nuevo_label(f_item, texto_paq, fuente=("Arial", 11, "bold"), color_texto=color_paq, poscicion="center").grid(row=0, column=4, sticky="nsew", pady=10)
            
            # Botones de Acción (Editar y Habilitar/Deshabilitar)
            frame_btn = nuevo_frame(f_item, color_fondo="transparent")
            frame_btn.grid(row=0, column=5, sticky="nsew", padx=5, pady=5)
            
            # Botón Editar
            criterio_busqueda = prod.get('codigo_barras') if prod.get('codigo_barras') else prod.get('nombre', '')
            nuevo_boton(frame_btn, "Editar", comando=lambda c=criterio_busqueda: self.winfo_toplevel().mostrar_editar(c), color_fondo="#3498db", color_hover="#2980b9", ancho=65).pack(side="left", padx=2, expand=True)

            if prod['activo']:
                nuevo_boton(frame_btn, "X", comando=lambda id=prod['id'], n=prod['nombre']: self.confirmar_cambio_estado(id, n, False), color_fondo=COLOR_FALLO, color_hover=COLOR_FALLO_HOVER, ancho=35).pack(side="right", padx=2, expand=True)
            else:
                nuevo_boton(frame_btn, "✓", comando=lambda id=prod['id'], n=prod['nombre']: self.confirmar_cambio_estado(id, n, True), color_fondo=COLOR_EXITO, color_hover=COLOR_EXITO_HOVER, ancho=35).pack(side="right", padx=2, expand=True)

        # --- ALERTA DE STOCK NEGATIVO O CERO ---
        if any(p['stock'] <= 0 for p in productos):
            self.lbl_alerta_stock = nuevo_label(self.frame_tabla_container, "⚠️ ¡ALERTA! Existen productos con stock en 0 o negativo. Se requiere reabastecimiento urgente.", color_texto=COLOR_FALLO, fuente=("Arial", 13, "bold"))
            self.lbl_alerta_stock.pack(pady=5)

    def confirmar_cambio_estado(self, producto_id, nombre_producto, es_activacion):
        ModalConfirmacionEstado(self, nombre_producto, es_activacion, lambda: self.ejecutar_cambio_estado(producto_id, es_activacion))

    def ejecutar_cambio_estado(self, producto_id, es_activacion):
        exito, mensaje = reactivar_producto_db(producto_id) if es_activacion else desactivar_producto_db(producto_id)
        self.lbl_mensaje.configure(text=mensaje, text_color=COLOR_EXITO if exito else COLOR_FALLO)
        if exito: self.cargar_inventario()