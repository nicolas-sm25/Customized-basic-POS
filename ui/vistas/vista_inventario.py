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

        # --- CABECERA DE LA TABLA ---
        f_enc = nuevo_frame(self.scroll_tabla, color_fondo="#1a1a1a")
        f_enc.pack(fill="x", pady=(0, 5), padx=5)
        
        f_enc.grid_columnconfigure(0, weight=3, uniform="inv")
        f_enc.grid_columnconfigure(1, weight=2, uniform="inv")
        f_enc.grid_columnconfigure(2, weight=2, uniform="inv")
        f_enc.grid_columnconfigure(3, weight=2, uniform="inv")
        f_enc.grid_columnconfigure(4, weight=3, uniform="inv")
        f_enc.grid_columnconfigure(5, weight=1, uniform="inv")
        
        nuevo_label(f_enc, "Producto", fuente=("Arial", 14, "bold"), color_texto="#a0a0a0", poscicion="w").grid(row=0, column=0, sticky="w", padx=10, pady=8)
        nuevo_label(f_enc, "Costo", fuente=("Arial", 14, "bold"), color_texto="#a0a0a0", poscicion="e").grid(row=0, column=1, sticky="e")
        nuevo_label(f_enc, "Precio Venta", fuente=("Arial", 14, "bold"), color_texto="#a0a0a0", poscicion="e").grid(row=0, column=2, sticky="e")
        nuevo_label(f_enc, "Stock", fuente=("Arial", 14, "bold"), color_texto="#a0a0a0", poscicion="center").grid(row=0, column=3, sticky="nsew")
        nuevo_label(f_enc, "Paquete de", fuente=("Arial", 14, "bold"), color_texto="#a0a0a0", poscicion="center").grid(row=0, column=4, sticky="nsew")
        nuevo_label(f_enc, "Acción", fuente=("Arial", 14, "bold"), color_texto="#a0a0a0", poscicion="center").grid(row=0, column=5, sticky="nsew", padx=5)

        # --- FILAS DE PRODUCTOS ---
        for prod in productos:
            color_fondo_fila = "#2b2b2b" if prod['activo'] else "#1c1c1c"
            f_item = nuevo_frame(self.scroll_tabla, color_fondo=color_fondo_fila)
            f_item.pack(fill="x", pady=4, padx=5)
            
            f_item.grid_columnconfigure(0, weight=3, uniform="inv")
            f_item.grid_columnconfigure(1, weight=2, uniform="inv")
            f_item.grid_columnconfigure(2, weight=2, uniform="inv")
            f_item.grid_columnconfigure(3, weight=2, uniform="inv")
            f_item.grid_columnconfigure(4, weight=3, uniform="inv")
            f_item.grid_columnconfigure(5, weight=1, uniform="inv")

            # Nombre
            nombre_mostrar = prod['nombre'] if prod['activo'] else f"{prod['nombre']} (Inactivo)"
            color_nombre = "#4fa6ff" if prod['activo'] else "#666666"
            nuevo_label(f_item, nombre_mostrar, fuente=("Arial", 14, "bold" if prod['activo'] else "normal"), color_texto=color_nombre, poscicion="w").grid(row=0, column=0, sticky="w", padx=10, pady=10)
            
            # Costo
            nuevo_label(f_item, f"${int(prod['costo']):,}".replace(",", "."), fuente=("Arial", 13), color_texto="#888888" if not prod['activo'] else "#cccccc").grid(row=0, column=1, sticky="e", pady=10)
            
            # Precio Venta
            nuevo_label(f_item, f"${int(prod['precio_venta']):,}".replace(",", "."), fuente=("Arial", 13, "bold"), color_texto="#448844" if not prod['activo'] else COLOR_EXITO).grid(row=0, column=2, sticky="e", pady=10)
            
            # Stock
            if prod['stock'] <= 5:
                color_stock = COLOR_FALLO
                texto_stock = f"{prod['stock']} ⚠️"
            else:
                color_stock = "#ffffff" if prod['activo'] else "#888888"
                texto_stock = str(prod['stock'])
                
            nuevo_label(f_item, texto_stock, fuente=("Arial", 14, "bold"), color_texto=color_stock, poscicion="center").grid(row=0, column=3, sticky="nsew", pady=10)
            
            # Relación
            if prod['unidad_inactiva']:
                texto_paq = f"{prod['info_paquete']} ⚠️ (Unidad Inactiva)"
                color_paq = COLOR_FALLO
            else:
                texto_paq = prod['info_paquete']
                color_paq = "#d4ac0d" if prod['es_paquete'] else "#666666"

            nuevo_label(f_item, texto_paq, fuente=("Arial", 11, "bold"), color_texto=color_paq, poscicion="center").grid(row=0, column=4, sticky="nsew", pady=10)
            
            # Botón de Acción (X para desactivar, o ✓ para reactivar)
            frame_btn = nuevo_frame(f_item, color_fondo="transparent")
            frame_btn.grid(row=0, column=5, sticky="nsew", padx=5, pady=5)
            
            if prod['activo']:
                btn_desactivar = nuevo_boton(
                    frame_btn, 
                    "X", 
                    comando=lambda p_id=prod['id'], p_nombre=prod['nombre']: self.confirmar_cambio_estado(p_id, p_nombre, es_activacion=False), 
                    color_fondo=COLOR_FALLO, 
                    color_hover=COLOR_FALLO_HOVER, 
                    ancho=40
                )
                btn_desactivar.pack(expand=True)
            else:
                btn_reactivar = nuevo_boton(
                    frame_btn, 
                    "✓", 
                    comando=lambda p_id=prod['id'], p_nombre=prod['nombre']: self.confirmar_cambio_estado(p_id, p_nombre, es_activacion=True), 
                    color_fondo=COLOR_EXITO, 
                    color_hover=COLOR_EXITO_HOVER, 
                    ancho=40
                )
                btn_reactivar.pack(expand=True)

    def confirmar_cambio_estado(self, producto_id, nombre_producto, es_activacion):
        """Abre el modal unificado de confirmación (activar o desactivar)."""
        ModalConfirmacionEstado(self, nombre_producto, es_activacion, lambda: self.ejecutar_cambio_estado(producto_id, es_activacion))

    def ejecutar_cambio_estado(self, producto_id, es_activacion):
        """Llama al BLL correspondiente según la acción y recarga la tabla."""
        if es_activacion:
            exito, mensaje = reactivar_producto_db(producto_id)
        else:
            exito, mensaje = desactivar_producto_db(producto_id)

        if exito:
            self.lbl_mensaje.configure(text=mensaje, text_color=COLOR_EXITO)
            self.cargar_inventario()
        else:
            self.lbl_mensaje.configure(text=mensaje, text_color=COLOR_FALLO)