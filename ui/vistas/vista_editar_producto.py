from bll.gestor_productos import buscar_producto_por_codigo, buscar_productos_por_nombre, actualizar_producto
from ui.componentes.configuracion_componentes import ConfiguracionComponentes
from ui.componentes.creador_componentes import *

class VistaEditarProducto(ConfiguracionComponentes):
    def __init__(self, master):
        super().__init__(master)
        
        # --- TÍTULO ---
        self.lbl_titulo = nuevo_label(self, "Buscar y Editar Producto", fuente=FUENTE_TITULOS)
        self.lbl_titulo.pack(pady=15)
        
        
        # --- BÚSQUEDA DE PRODUCTOS ---
        self.frame_busqueda = nuevo_frame(self)
        self.frame_busqueda.pack(pady=5)

        self.entry_busqueda = nueva_caja_texto(self.frame_busqueda, placeholder="Código o Nombre...")
        self.entry_busqueda.grid(row=0, column=0, padx=5)
        self.entry_busqueda.bind("<Return>", self.buscar_producto)

        self.btn_buscar = nuevo_boton(self.frame_busqueda, "Buscar", comando=self.buscar_producto)
        self.btn_buscar.grid(row=0, column=1, padx=5)

        # --- INFO PRINCIPAL DE PRODUCTOS ---
        self.frame_edicion = nuevo_frame(self)
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
        
        # --- BOTONES ---
        self.frame_botones = nuevo_frame(self)
        self.frame_botones.pack(pady=10)

        self.btn_guardar = nuevo_boton(self.frame_botones, "Guardar Cambios", comando=self.guardar_cambios, color_fondo=COLOR_EXITO, color_hover=COLOR_EXITO_HOVER)
        self.btn_guardar.grid(row=0, column=0, padx=10)
        self.btn_guardar.configure(state="disabled")

        self.btn_cancelar = nuevo_boton(self.frame_botones, "Cancelar", lambda: self.reiniciar_pantalla("Edición cancelada.", COLOR_FALLO), color_fondo=COLOR_FALLO, color_hover=COLOR_FALLO_HOVER)
        self.btn_cancelar.grid(row=0, column=1, padx=10)
        self.btn_cancelar.configure(state="disabled")

        # --- MENSAJE DE ESTADO ---
        self.lbl_mensaje = nuevo_label(self, "")
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
        
    # --- MOSTRAR RESULTADOS DE LA BUSQUEDA EN PANTALLA ---    
    def cargar_datos_en_pantalla(self, producto):
            self.limpiar_campos()
            
            self.lbl_valor_nombre.configure(text=producto["nombre"])
            self.lbl_valor_codigo.configure(text=producto["codigo_barras"] if producto["codigo_barras"] else "N/A")
            
            self.habilitar(self.entradas_editables)
            self.entry_costo.insert(0, str(int(producto["costo"])))
            self.entry_precio.insert(0, str(int(producto["precio_venta"])))
            self.entry_stock.insert(0, str(producto["stock"]))

    # --- BÚSQUEDA DE PRODUCTOS EN LA DB ---
    def buscar_producto(self, event=None):
        criterio = self.entry_busqueda.get().strip()
        if not criterio:
            return

        producto = buscar_producto_por_codigo(criterio)

        if not producto:
            resultados = buscar_productos_por_nombre(criterio)
            if resultados:
                producto = resultados[0] 

        if producto:
            self.producto_id_actual = producto["id"]
            self.nombre_actual = producto["nombre"]
            self.codigo_actual = producto["codigo_barras"]
            
            self.deshabilitar(self.elementos_busqueda)
            self.cargar_datos_en_pantalla(producto)
            self.habilitar(self.entradas_editables, self.botones_accion)
            
            self.lbl_mensaje.configure(text="Producto cargado. Ya puede editar costos y stock.", text_color=COLOR_EXITO)
            self.entry_costo.focus()
        else:
            self.reiniciar_pantalla(mensaje="No se encontró ningún producto.", color=COLOR_FALLO)

    # --- GUARDAR NUEVA INFO EN LA DB ---
    def guardar_cambios(self, event=None):
        if not self.producto_id_actual:
            return

        costo_str = self.entry_costo.get().replace(".", "").strip()
        precio_str = self.entry_precio.get().replace(".", "").strip()
        stock_str = self.entry_stock.get().replace(".", "").strip()

        if not costo_str or not precio_str:
            self.lbl_mensaje.configure(text="El costo y el precio son obligatorios.", text_color=COLOR_FALLO)
            return

        try:
            costo = float(costo_str)
            precio = float(precio_str)
            stock = int(stock_str) if stock_str else 0

            if costo < 0 or precio < 0 or stock < 0:
                self.lbl_mensaje.configure(text="No se admiten valores negativos.", text_color=COLOR_FALLO)
                return

            exito, mensaje = actualizar_producto(
                self.producto_id_actual, 
                self.nombre_actual, 
                costo, 
                precio, 
                self.codigo_actual, 
                stock
            )

            if exito:
                self.reiniciar_pantalla(mensaje="Cambios guardados exitosamente.", color=COLOR_EXITO)
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
        
        self.entry_busqueda.delete(0, 'end')
        self.entry_busqueda.focus()
        
        self.lbl_mensaje.configure(text=mensaje, text_color=color)