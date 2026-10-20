import customtkinter as ctk
from ui.vista_productos import VistaAgregarProducto

class VentanaPrincipal(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Sistema POS - Mi Tienda")
        self.geometry("900x600")
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        self.frame_menu = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.frame_menu.grid(row=0, column=0, sticky="nsew")
        self.frame_menu.grid_rowconfigure(4, weight=1)
        
        self.lbl_logo = ctk.CTkLabel(self.frame_menu, text="TIENDA", font=("Arial", 24, "bold"))
        self.lbl_logo.grid(row=0, column=0, padx=20, pady=30)
        
        self.btn_caja = ctk.CTkButton(self.frame_menu, text="Caja", command=self.mostrar_caja)
        self.btn_caja.grid(row=1, column=0, padx=20, pady=10)
        
        self.btn_productos = ctk.CTkButton(self.frame_menu, text="Gestión Productos", command=self.mostrar_productos)
        self.btn_productos.grid(row=2, column=0, padx=20, pady=10)
        
        self.frame_contenido = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.frame_contenido.grid(row=0, column=1, sticky="nsew")
        
        self.vista_actual = None
        
        self.mostrar_productos()

    def cambiar_vista(self, nueva_vista_clase):
        if self.vista_actual:
            self.vista_actual.destroy()
            
        self.vista_actual = nueva_vista_clase(self.frame_contenido)
        self.vista_actual.pack(fill="both", expand=True, padx=20, pady=20)

    def mostrar_productos(self):
        self.cambiar_vista(VistaAgregarProducto)

    def mostrar_caja(self):
        if self.vista_actual:
            self.vista_actual.destroy()
            
        self.vista_actual = ctk.CTkLabel(self.frame_contenido, text="Pantalla de Caja (En construcción)", font=("Arial", 24))
        self.vista_actual.pack(expand=True)