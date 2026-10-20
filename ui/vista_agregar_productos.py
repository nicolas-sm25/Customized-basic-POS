import customtkinter as ctk
from bll.gestor_productos import agregar_producto

class VistaAgregarProducto(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.lbl_titulo = ctk.CTkLabel(self, text="Agregar Producto", font=("Arial", 20, "bold"))
        self.lbl_titulo.pack(pady=15)

        self.entry_nombre = ctk.CTkEntry(self, placeholder_text="Nombre del producto", width=250)
        self.entry_nombre.pack(pady=10)

        self.entry_codigo = ctk.CTkEntry(self, placeholder_text="Código de Barras (Opcional)", width=250)
        self.entry_codigo.pack(pady=10)

        self.entry_costo = ctk.CTkEntry(self, placeholder_text="Costo", width=250)
        self.entry_costo.pack(pady=10)

        self.entry_precio = ctk.CTkEntry(self, placeholder_text="Precio de Venta", width=250)
        self.entry_precio.pack(pady=10)

        self.entry_stock = ctk.CTkEntry(self, placeholder_text="Stock Inicial", width=250)
        self.entry_stock.pack(pady=10)

        self.btn_guardar = ctk.CTkButton(self, text="Guardar Producto", command=self.guardar_producto)
        self.btn_guardar.pack(pady=20)

        self.lbl_mensaje = ctk.CTkLabel(self, text="")
        self.lbl_mensaje.pack(pady=5)

    def guardar_producto(self):
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

            exito, mensaje = agregar_producto(nombre, costo, precio, codigo, stock)

            if exito:
                self.lbl_mensaje.configure(text=mensaje, text_color="green")
                self.limpiar_campos()
            else:
                self.lbl_mensaje.configure(text=mensaje, text_color="red")

        except ValueError:
            self.lbl_mensaje.configure(text="Costo, precio y stock deben ser números.", text_color="red")

    def limpiar_campos(self):
        self.entry_nombre.delete(0, 'end')
        self.entry_codigo.delete(0, 'end')
        self.entry_costo.delete(0, 'end')
        self.entry_precio.delete(0, 'end')
        self.entry_stock.delete(0, 'end')