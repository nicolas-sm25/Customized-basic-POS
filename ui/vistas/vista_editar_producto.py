from bll.gestor_productos import *
from ui.componentes.configuracion_componentes import ConfiguracionComponentes
from ui.componentes.creador_componentes import *
from ui.vistas.secciones.panel_autocompletado import PanelAutocompletado

class VistaEditarProducto(ConfiguracionComponentes):
    def __init__(self, master):
        super().__init__(master)

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.frame_central = nuevo_frame(self, color_fondo="transparent")
        self.frame_central.grid(row=1, column=0)
        
        # --- TÍTULO ---
        self.lbl_titulo = nuevo_label(self.frame_central, "Buscar y Editar Producto", fuente=FUENTE_TITULOS)
        self.lbl_titulo.pack(pady=15)
        
        # --- BÚSQUEDA DE PRODUCTOS ---
        self.frame_busqueda = nuevo_frame(self.frame_central)
        self.frame_busqueda.pack(pady=5)

        self.entry_busqueda = nueva_caja_texto(self.frame_busqueda, placeholder="Código o Nombre...")
        self.entry_busqueda.grid(row=0, column=0, padx=5)
        self.entry_busqueda.bind("<Return>", self.buscar_producto)

        self.btn_buscar = nuevo_boton(self.frame_busqueda, "Buscar", comando=self.buscar_producto)
        self.btn_buscar.grid(row=0, column=1, padx=5)

        # --- INFO PRINCIPAL DE PRODUCTOS ---
        self.frame_edicion = nuevo_frame(self.frame_central)
        self.frame_edicion.pack(pady=15)

        # --- AUTOCOMPLETADO ---
        self.autocompletado = PanelAutocompletado(self.entry_busqueda, self.frame_central, self.frame_edicion, self.resultado_autocompletado)
        
        # --- INFO PRINCIPAL DE PRODUCTOS ---
        self.frame_edicion = nuevo_frame(self.frame_central)
        self.frame_edicion.pack(pady=15)

        self.lbl_nombre = nuevo_label(self.frame_edicion, "Nombre:", fuente=FUENTE_NEGRITA, poscicion="e")
        self.lbl_nombre.grid(row=0, column=0, padx=5, pady=5)
        self.lbl_valor_nombre = nuevo_label(self.frame_edicion, "-", poscicion="w")
        self.lbl_valor_nombre.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        self.lbl_codigo = nuevo_label(self.frame_edicion, "Código de Barras:", fuente=FUENTE_NEGRITA, poscicion="e")
        self.lbl_codigo.grid(row=1, column=0, padx=5, pady=5)
        self.lbl_valor_codigo = nuevo_label(self.frame_edicion, "-", poscicion="w")
        self.lbl_valor_codigo.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        # --- ACTUALIZAR INFO ---
        self.lbl_costo = nuevo_label(self.frame_edicion, "Costo:", poscicion="e")
        self.lbl_costo.grid(row=2, column=0, padx=5, pady=5)
        self.entry_costo = nueva_caja_texto(self.frame_edicion)
        self.entry_costo.grid(row=2, column=1, padx=5, pady=5)
        self.entry_costo.configure(state="disabled")
        self.entry_costo.bind("<KeyRelease>", lambda event: self.formatear_entrada_moneda(self.entry_costo)) 
        self.entry_costo.bind("<Return>", lambda event: self.entry_precio.focus())
        self.entry_costo.bind("<Escape>", lambda event: self.reiniciar_pantalla("Edición cancelada.", COLOR_FALLO))

        self.lbl_precio = nuevo_label(self.frame_edicion, "Precio de Venta:", poscicion="e")
        self.lbl_precio.grid(row=3, column=0, padx=5, pady=5)
        self.entry_precio = nueva_caja_texto(self.frame_edicion)
        self.entry_precio.grid(row=3, column=1, padx=5, pady=5)
        self.entry_precio.configure(state="disabled")
        self.entry_precio.bind("<KeyRelease>", lambda event: self.formatear_entrada_moneda(self.entry_precio)) 
        self.entry_precio.bind("<Return>", lambda event: self.entry_stock.focus())
        self.entry_precio.bind("<Escape>", lambda event: self.reiniciar_pantalla("Edición cancelada.", COLOR_FALLO))

        self.lbl_stock = nuevo_label(self.frame_edicion, "Stock:", poscicion="e")
        self.lbl_stock.grid(row=4, column=0, padx=5, pady=5)
        self.entry_stock = nueva_caja_texto(self.frame_edicion)
        self.entry_stock.grid(row=4, column=1, padx=5, pady=5)
        self.entry_stock.configure(state="disabled")
        self.entry_stock.bind("<KeyRelease>", lambda event: self.formatear_entrada_moneda(self.entry_stock)) 
        self.entry_stock.bind("<Return>", self.guardar_cambios)
        self.entry_stock.bind("<Escape>", lambda event: self.reiniciar_pantalla("Edición cancelada.", COLOR_FALLO))

        self.lbl_info_paquete = nuevo_label(self.frame_edicion, "", color_texto="#4fa6ff", fuente=("Arial", 12, "bold"))
        self.lbl_info_paquete.grid(row=5, column=0, columnspan=2, pady=(5, 5))
        self.lbl_info_paquete.grid_remove()

        # --- BOTONES ---
        self.frame_botones = nuevo_frame(self.frame_central)
        self.frame_botones.pack(pady=10)

        self.btn_guardar = nuevo_boton(self.frame_botones, "Guardar Cambios (Enter)", comando=self.guardar_cambios, color_fondo=COLOR_EXITO, color_hover=COLOR_EXITO_HOVER)
        self.btn_guardar.grid(row=0, column=0, padx=10)
        self.btn_guardar.configure(state="disabled")

        self.btn_cancelar = nuevo_boton(self.frame_botones, "Cancelar (ESC)", lambda: self.reiniciar_pantalla("Edición cancelada.", COLOR_FALLO), color_fondo=COLOR_FALLO, color_hover=COLOR_FALLO_HOVER)
        self.btn_cancelar.grid(row=0, column=1, padx=10)
        self.btn_cancelar.configure(state="disabled")
        self.winfo_toplevel().bind("<Escape>", lambda event: self.reiniciar_pantalla("Edición cancelada.", COLOR_FALLO))

        self.btn_edicion_avanzada = nuevo_boton(self.frame_botones, "Edición Avanzada", comando=self.abrir_modal_avanzado, color_fondo="#5e17eb", color_hover="#4a11c0", ancho=250)
        self.btn_edicion_avanzada.grid(row=1, column=0, columnspan=2, pady=(15, 0))
        self.btn_edicion_avanzada.configure(state="disabled")

        # --- MENSAJE DE ESTADO ---
        self.lbl_mensaje = nuevo_label(self.frame_central, "")
        self.lbl_mensaje.pack(pady=5)

        # --- LISTA DE ENTRADAS EDITABLES PARA LIMPIEZA Y BLOQUEO ---
        self.entradas_editables = [self.entry_costo, self.entry_precio, self.entry_stock]
        self.labels_estaticos = [self.lbl_valor_nombre, self.lbl_valor_codigo]
        self.botones_accion = [self.btn_guardar, self.btn_cancelar]
        self.elementos_busqueda = [self.entry_busqueda, self.btn_buscar]
        
        # --- VARIABLES DE ESTADO ---
        self.producto_id_actual = None
        self.nombre_actual = None
        self.codigo_actual = None
        
    # --- MOSTRAR RESULTADOS Y APLICAR RESTRICCIONES POR ROL ---    
    def cargar_datos_en_pantalla(self, producto):
        self.limpiar_campos()
        self.stock_actual = producto["stock"] 
        
        self.lbl_valor_nombre.configure(text=producto["nombre"])
        self.lbl_valor_codigo.configure(text=producto["codigo_barras"] if producto["codigo_barras"] else "N/A")

        self.habilitar(self.entradas_editables)

        self.entry_costo.insert(0, str(int(producto["costo"])))
        self.entry_precio.insert(0, str(int(producto["precio_venta"])))
        self.entry_stock.insert(0, str(producto["stock"]))

        # --- LÓGICA DE PAQUETE RELACIONAL ---
        datos_completos = obtener_producto_por_id(producto["id"])
        if datos_completos and datos_completos.get("es_paquete"):
            base_id = datos_completos.get("producto_base_id")
            cant = datos_completos.get("cantidad_por_paquete")
            unitarios = obtener_productos_unitarios()

            nombre_base = next((u["nombre"] for u in unitarios if u["id"] == base_id), "Desconocida/Eliminada")

            self.lbl_info_paquete.configure(text=f"Paquete de {nombre_base} | Cant. por paquete: {cant}")
            self.lbl_info_paquete.grid()
        else:
            self.lbl_info_paquete.grid_remove()

        rol_usuario = self.winfo_toplevel().usuario_actual['rol']

        if rol_usuario == "Vendedor":
            self.entry_costo.configure(state="disabled")
            self.entry_precio.configure(state="disabled")
            self.btn_edicion_avanzada.configure(state="disabled", text="Edición Avanzada (🔒 Solo Admin)", text_color=COLOR_FALLO)
        else:
            self.btn_edicion_avanzada.configure(state="normal", text="Edición Avanzada")

    def buscar_externamente(self, criterio):
        """Llamado desde el inventario para auto-buscar el producto."""
        self.entry_busqueda.delete(0, 'end')
        self.entry_busqueda.insert(0, criterio)
        self.buscar_producto()

    # --- BÚSQUEDA DE PRODUCTOS EN LA DB ---
    def buscar_producto(self, event=None):
        if self.autocompletado.procesar_enter(): return
        
        criterio = self.entry_busqueda.get().strip()
        if not criterio:
            return

        producto = buscar_producto_por_codigo(criterio)
        if not producto:
            resultados = buscar_productos_por_nombre(criterio)
            if resultados:

                producto_exacto = next((p for p in resultados if p['nombre'].lower() == criterio.lower()), None)
                producto = producto_exacto if producto_exacto else resultados[0] 

        if producto:
            self.procesar_carga_producto(producto)
        else:
            self.reiniciar_pantalla("No se encontró ningún producto.", COLOR_FALLO)

    def procesar_carga_producto(self, producto):
        """Aísla la validación y carga. Evita re-consultar a la BD si ya tenemos el objeto."""
        if not producto.get('activo', True):
            self.reiniciar_pantalla("Este producto se encuentra inhabilitado, habilitelo desde el menú inventario para editarlo.", color="#d4ac0d")
            return

        ventana_ppal = self.winfo_toplevel()
        if hasattr(ventana_ppal, 'carrito_guardado') and ventana_ppal.carrito_guardado:
            for item in ventana_ppal.carrito_guardado:
                if item['id'] == producto['id']:
                    self.reiniciar_pantalla("No se puede editar un producto que está actualmente en el carrito de compras.", color="#d4ac0d")
                    return

        self.producto_id_actual = producto["id"]
        self.nombre_actual = producto["nombre"]
        self.codigo_actual = producto["codigo_barras"]
        self.deshabilitar(self.elementos_busqueda)
        
        self.cargar_datos_en_pantalla(producto)
        self.habilitar(self.botones_accion)
        
        self.lbl_mensaje.configure(text="Producto cargado.", text_color=COLOR_EXITO)
        self.entry_stock.focus()

    def resultado_autocompletado(self, producto):
        """Se activa cuando el autocompletado devuelve un producto."""
        self.entry_busqueda.delete(0, 'end')
        self.entry_busqueda.insert(0, producto['codigo_barras'] if producto['codigo_barras'] else producto['nombre'])

        self.procesar_carga_producto(producto)

    def abrir_modal_avanzado(self):
        if not self.producto_id_actual: return
        from ui.modales.modal_edicion_avanzada import ModalEdicionAvanzada
        ModalEdicionAvanzada(self.winfo_toplevel(), self.producto_id_actual, self.al_cerrar_modal_avanzado)
        
    def al_cerrar_modal_avanzado(self, exito, mensaje, fue_eliminado, nuevo_nombre, nuevo_codigo, es_cambio_estado=False):
        """Se ejecuta cuando el modal se cierra exitosamente."""
        if exito:
            if fue_eliminado:
                self.reiniciar_pantalla("Producto eliminado definitivamente.", COLOR_EXITO)
            elif es_cambio_estado:
                self.reiniciar_pantalla(mensaje, COLOR_EXITO)
            else:
                self.lbl_mensaje.configure(text=mensaje, text_color=COLOR_EXITO)
                self.nombre_actual = nuevo_nombre
                self.codigo_actual = nuevo_codigo
                self.lbl_valor_nombre.configure(text=nuevo_nombre)
                self.lbl_valor_codigo.configure(text=nuevo_codigo if nuevo_codigo else "N/A")
                self.buscar_externamente(nuevo_codigo if nuevo_codigo else nuevo_nombre)

    # --- GUARDAR NUEVA INFO EN LA DB (CON VALIDACIÓN DE ROL) ---
    def guardar_cambios(self, event=None):
        if not self.producto_id_actual:
            return

        costo_str = self.entry_costo.get().replace(".", "").strip()
        precio_str = self.entry_precio.get().replace(".", "").strip()
        stock_str = self.entry_stock.get().replace(".", "").strip()

        try:
            costo = float(costo_str) if costo_str else 0
            precio = float(precio_str) if precio_str else 0
            stock = int(stock_str) if stock_str else 0

            if costo < 0 or precio < 0 or stock < 0:
                self.lbl_mensaje.configure(text="Los valores numéricos (Precio/Stock) no pueden ser negativos.", text_color=COLOR_FALLO)
                return

            if precio == 0:
                self.lbl_mensaje.configure(text="El precio de venta no puede ser $0.", text_color=COLOR_FALLO)
                return

            if costo >= precio:
                self.lbl_mensaje.configure(text="El costo no puede ser mayor o igual que el precio de venta.", text_color=COLOR_FALLO)
                return

            rol_usuario = self.winfo_toplevel().usuario_actual['rol']

            if rol_usuario == "Vendedor":
                if stock < self.stock_actual:
                    self.lbl_mensaje.configure(text="Los vendedores solo pueden registrar entradas (aumentar stock).", text_color=COLOR_FALLO)
                    return

            exito, mensaje = actualizar_producto(
                self.producto_id_actual, self.nombre_actual, costo, precio, self.codigo_actual, stock
            )

            if exito:
                msj = "Cambios guardados." if costo > 0 else "Advertencia: Producto guardado con costo $0."
                self.reiniciar_pantalla(msj, "#d4ac0d" if costo == 0 else COLOR_EXITO)
            else:
                self.lbl_mensaje.configure(text=mensaje, text_color=COLOR_FALLO)

        except ValueError:
            self.lbl_mensaje.configure(text="Costo, precio y stock deben ser números.", text_color=COLOR_FALLO)


    # --- RESETEO AL ESTADO INICIAL DE BUSQUEDA ---
    def reiniciar_pantalla(self, mensaje="Edición finalizada.", color="gray"):
        
        self.producto_id_actual = None
        self.nombre_actual = None
        self.codigo_actual = None
        
        self.limpiar_campos()
        self.deshabilitar(self.entradas_editables, self.botones_accion)
        self.habilitar(self.elementos_busqueda)
        self.btn_edicion_avanzada.configure(state="disabled")

        self.lbl_info_paquete.grid_remove()

        self.entry_busqueda.delete(0, 'end')
        self.entry_busqueda.focus()
        
        self.lbl_mensaje.configure(text=mensaje, text_color=color)

    # --- DESHABILITADOR DE ATAJOS ---
    def destroy(self):
        """Se ejecuta al cambiar de vista. Limpia los atajos de teclado globales."""
        try:
            self.winfo_toplevel().unbind("<Escape>")
        except Exception:
            pass
        super().destroy()