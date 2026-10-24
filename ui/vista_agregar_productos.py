from bll.gestor_productos import agregar_producto
from ui.configuracion_componentes import ConfiguracionComponentes
from ui.creador_componentes import *

class VistaAgregarProducto(ConfiguracionComponentes):
    def __init__(self, master):
        super().__init__(master)
        
        # --- TÍTULO ---
        self.lbl_titulo = nuevo_label(self, "Agregar Producto", fuente=FUENTE_TITULOS)
        self.lbl_titulo.pack(pady=15)

        # --- ENTRADAS DE DATOS ---
        self.entry_nombre = nueva_caja_texto(self, placeholder="Nombre del producto")
        self.entry_nombre.pack(pady=10)
        self.entry_nombre.bind("<Return>", lambda event: self.entry_codigo.focus())
        self.entry_nombre.bind("<Escape>", lambda event: self.cancelar_registro())

        self.entry_codigo = nueva_caja_texto(self, placeholder="Código de Barras (Opcional)")
        self.entry_codigo.pack(pady=10)
        self.entry_codigo.bind("<Return>", lambda event: self.entry_costo.focus())
        self.entry_codigo.bind("<Escape>", lambda event: self.cancelar_registro())

        self.entry_costo = nueva_caja_texto(self, placeholder="Costo")
        self.entry_costo.pack(pady=10)
        self.entry_costo.bind("<Return>", lambda event: self.entry_precio.focus())
        self.entry_costo.bind("<Escape>", lambda event: self.cancelar_registro())
        
        self.entry_precio = nueva_caja_texto(self, placeholder="Precio de Venta")
        self.entry_precio.pack(pady=10)
        self.entry_precio.bind("<Return>", lambda event: self.entry_stock.focus())
        self.entry_precio.bind("<Escape>", lambda event: self.cancelar_registro())
        
        self.entry_stock = nueva_caja_texto(self, placeholder="Stock Inicial")
        self.entry_stock.pack(pady=10)
        self.entry_stock.bind("<Return>", self.guardar_producto)
        self.entry_stock.bind("<Escape>", lambda event: self.cancelar_registro())
        
        # --- BOTONES ---
        self.frame_botones = nuevo_frame(self)
        self.frame_botones.pack(pady=20)

        self.btn_guardar = nuevo_boton(self.frame_botones, "Guardar Producto", self.guardar_producto, color_fondo=COLOR_EXITO, color_hover=COLOR_EXITO_HOVER)
        self.btn_guardar.grid(row=0, column=0, padx=10)

        self.btn_cancelar = nuevo_boton(self.frame_botones, "Cancelar", self.cancelar_registro, color_fondo=COLOR_FALLO, color_hover=COLOR_FALLO_HOVER)
        self.btn_cancelar.grid(row=0, column=1, padx=10)
        
        # --- MENSAJE DE ESTADO ---
        self.lbl_mensaje = nuevo_label(self, "")
        self.lbl_mensaje.pack(pady=5)
        
        # --- LISTA DE ENTRADAS EDITABLES PARA LIMPIEZA Y BLOQUEO ---
        self.entradas_editables = [
            self.entry_nombre, self.entry_codigo, self.entry_costo, 
            self.entry_precio, self.entry_stock
        ]

    # --- AÑADIR PRODUCTO A LA DB ---
    def guardar_producto(self, event=None): 
        nombre = self.entry_nombre.get()
        codigo = self.entry_codigo.get()
        costo_str = self.entry_costo.get()
        precio_str = self.entry_precio.get()
        stock_str = self.entry_stock.get()

        if not nombre or not costo_str or not precio_str:
            self.lbl_mensaje.configure(text="Nombre, costo y precio son obligatorios.", text_color="red")
            return

        try:
            costo = float(costo_str)
            precio = float(precio_str)
            stock = int(stock_str) if stock_str else 0
            codigo = codigo if codigo else None

            if costo <= 0 or precio <= 0 or stock < 0:
                self.lbl_mensaje.configure(text="Los valores numéricos no pueden ser negativos.", text_color="red")
                return
            
            if costo > precio:
                self.lbl_mensaje.configure(text="El costo no puede ser mayor que el precio de venta.", text_color="red")
                return

            exito, mensaje = agregar_producto(nombre, costo, precio, codigo, stock)

            if exito:
                self.lbl_mensaje.configure(text=mensaje, text_color="green")
                self.limpiar_campos()
                self.entry_nombre.focus()
            else:
                self.lbl_mensaje.configure(text=mensaje, text_color="red")

        except ValueError:
            self.lbl_mensaje.configure(text="Costo, precio y stock deben ser números.", text_color="red")
    
    # --- CANCELAR REGISTRO ---      
    def cancelar_registro(self):
        self.limpiar_campos()
        self.lbl_mensaje.configure(text="Registro cancelado.", text_color=COLOR_FALLO)
        self.after(1, self.entry_nombre.focus)