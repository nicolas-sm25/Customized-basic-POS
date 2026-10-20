import customtkinter as ctk
from bll.gestor_productos import buscar_producto_por_codigo, buscar_productos_por_nombre, actualizar_producto

class VistaEditarProducto(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.lbl_titulo = ctk.CTkLabel(self, text="Buscar y Editar Producto", font=("Arial", 20, "bold"))
        self.lbl_titulo.pack(pady=15)

        self.frame_busqueda = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_busqueda.pack(pady=5)

        self.entry_busqueda = ctk.CTkEntry(self.frame_busqueda, placeholder_text="Código o Nombre...", width=200)
        self.entry_busqueda.grid(row=0, column=0, padx=5)

        self.btn_buscar = ctk.CTkButton(self.frame_busqueda, text="Buscar", command=self.buscar_producto)
        self.btn_buscar.grid(row=0, column=1, padx=5)

        self.producto_id_actual = None
        self.nombre_actual = None
        self.codigo_actual = None

        self.frame_edicion = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_edicion.pack(pady=15)

        self.lbl_nombre = ctk.CTkLabel(self.frame_edicion, text="Nombre:", anchor="e", width=120, font=("Arial", 12, "bold"))
        self.lbl_nombre.grid(row=0, column=0, padx=5, pady=5)
        self.lbl_valor_nombre = ctk.CTkLabel(self.frame_edicion, text="-", anchor="w", width=250)
        self.lbl_valor_nombre.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        self.lbl_codigo = ctk.CTkLabel(self.frame_edicion, text="Código de Barras:", anchor="e", width=120, font=("Arial", 12, "bold"))
        self.lbl_codigo.grid(row=1, column=0, padx=5, pady=5)
        self.lbl_valor_codigo = ctk.CTkLabel(self.frame_edicion, text="-", anchor="w", width=250)
        self.lbl_valor_codigo.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        self.lbl_costo = ctk.CTkLabel(self.frame_edicion, text="Costo:", anchor="e", width=120)
        self.lbl_costo.grid(row=2, column=0, padx=5, pady=5)
        self.entry_costo = ctk.CTkEntry(self.frame_edicion, width=250, state="disabled")
        self.entry_costo.grid(row=2, column=1, padx=5, pady=5)

        self.lbl_precio = ctk.CTkLabel(self.frame_edicion, text="Precio de Venta:", anchor="e", width=120)
        self.lbl_precio.grid(row=3, column=0, padx=5, pady=5)
        self.entry_precio = ctk.CTkEntry(self.frame_edicion, width=250, state="disabled")
        self.entry_precio.grid(row=3, column=1, padx=5, pady=5)

        self.lbl_stock = ctk.CTkLabel(self.frame_edicion, text="Stock:", anchor="e", width=120)
        self.lbl_stock.grid(row=4, column=0, padx=5, pady=5)
        self.entry_stock = ctk.CTkEntry(self.frame_edicion, width=250, state="disabled")
        self.entry_stock.grid(row=4, column=1, padx=5, pady=5)

        self.frame_botones = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_botones.pack(pady=10)

        self.btn_guardar = ctk.CTkButton(self.frame_botones, text="Guardar Cambios", command=self.guardar_cambios, state="disabled", fg_color="green", hover_color="darkgreen")
        self.btn_guardar.grid(row=0, column=0, padx=10)

        self.btn_cancelar = ctk.CTkButton(self.frame_botones, text="Cancelar", command=self.cancelar_edicion, state="disabled", fg_color="red", hover_color="darkred")
        self.btn_cancelar.grid(row=0, column=1, padx=10)

        self.lbl_mensaje = ctk.CTkLabel(self, text="")
        self.lbl_mensaje.pack(pady=5)

    def buscar_producto(self):
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
            
            self.entry_busqueda.configure(state="disabled")
            self.btn_buscar.configure(state="disabled")
            
            self.cargar_datos_en_pantalla(producto)
            self.cambiar_estado_campos("normal")
            
            self.btn_guardar.configure(state="normal")
            self.btn_cancelar.configure(state="normal")
            self.lbl_mensaje.configure(text="Producto cargado. Ya puede editar costos y stock.", text_color="green")
        else:
            self.cancelar_edicion()
            self.lbl_mensaje.configure(text="No se encontró ningún producto.", text_color="red")

    def cargar_datos_en_pantalla(self, producto):
        self.limpiar_campos()
        
        self.lbl_valor_nombre.configure(text=producto["nombre"])
        self.lbl_valor_codigo.configure(text=producto["codigo_barras"] if producto["codigo_barras"] else "N/A")
        
        self.cambiar_estado_campos("normal")
        self.entry_costo.insert(0, str(producto["costo"]))
        self.entry_precio.insert(0, str(producto["precio_venta"]))
        self.entry_stock.insert(0, str(producto["stock"]))

    def guardar_cambios(self):
        if not self.producto_id_actual:
            return

        costo_str = self.entry_costo.get()
        precio_str = self.entry_precio.get()
        stock_str = self.entry_stock.get()

        if not costo_str or not precio_str:
            self.lbl_mensaje.configure(text="El costo y el precio son obligatorios.", text_color="red")
            return

        try:
            costo = float(costo_str)
            precio = float(precio_str)
            stock = int(stock_str) if stock_str else 0

            if costo < 0 or precio < 0 or stock < 0:
                self.lbl_mensaje.configure(text="No se admiten valores negativos.", text_color="red")
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
                self.lbl_mensaje.configure(text=mensaje, text_color="green")
                self.deshabilitar_edicion()
            else:
                self.lbl_mensaje.configure(text=mensaje, text_color="red")

        except ValueError:
            self.lbl_mensaje.configure(text="Costo, precio y stock deben ser números.", text_color="red")

    def cancelar_edicion(self):
        self.deshabilitar_edicion()
        self.lbl_mensaje.configure(text="Edición cancelada.", text_color="gray")

    def deshabilitar_edicion(self):
        self.producto_id_actual = None
        self.nombre_actual = None
        self.codigo_actual = None
        
        self.entry_busqueda.configure(state="normal")
        self.btn_buscar.configure(state="normal")
        self.entry_busqueda.delete(0, 'end')
        
        self.limpiar_campos()
        self.cambiar_estado_campos("disabled")
        
        self.btn_guardar.configure(state="disabled")
        self.btn_cancelar.configure(state="disabled")

    def limpiar_campos(self):
        # Limpiamos los labels
        self.lbl_valor_nombre.configure(text="-")
        self.lbl_valor_codigo.configure(text="-")
        
        # Limpiamos los entries
        self.cambiar_estado_campos("normal")
        self.entry_costo.delete(0, 'end')
        self.entry_precio.delete(0, 'end')
        self.entry_stock.delete(0, 'end')

    def cambiar_estado_campos(self, nuevo_estado):
        self.entry_costo.configure(state=nuevo_estado)
        self.entry_precio.configure(state=nuevo_estado)
        self.entry_stock.configure(state=nuevo_estado)