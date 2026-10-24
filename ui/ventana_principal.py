import customtkinter as ctk

from ui.creador_componentes import *
from ui.vista_agregar_productos import VistaAgregarProducto
from ui.vista_editar_producto import VistaEditarProducto

class VentanaPrincipal(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        
        # --- CONFIGURACIÓN PANTALLA PRINCIPAL ---
        self.title("Sistema POS - Mi Tienda")
        self.geometry("900x600")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        
        # --- MENÚ LATERAL ---
        self.frame_menu = nuevo_frame(self, color_fondo=None, radio_esquinas=0, ancho=200)
        self.frame_menu.grid(row=0, column=0, sticky="nsew")
        self.frame_menu.grid_rowconfigure(4, weight=1)
        
        self.lbl_logo = nuevo_label(self.frame_menu, "TIENDA", fuente=FUENTE_TITULOS)
        self.lbl_logo.grid(row=0, column=0, padx=20, pady=30)
        
        self.btn_caja = nuevo_boton(self.frame_menu, "Caja", comando=self.mostrar_caja)
        self.btn_caja.grid(row=1, column=0, padx=20, pady=10)
        
        self.btn_agregar = nuevo_boton(self.frame_menu, "Agregar Producto", comando=self.mostrar_agregar)
        self.btn_agregar.grid(row=2, column=0, padx=20, pady=10)
        
        self.btn_editar = nuevo_boton(self.frame_menu, "Editar Producto", comando=self.mostrar_editar)
        self.btn_editar.grid(row=3, column=0, padx=20, pady=10)
        
        # --- PANTALLA PREDETERMINADA TEMPORAL ---
        self.frame_contenido = nuevo_frame(self)
        self.frame_contenido.grid(row=0, column=1, sticky="nsew")
        self.vista_actual = None 
        self.mostrar_caja() # Caja es la pantalla predeterminada mientras se desarrolla

    # --- NAVEGACION ENTRE PANTALLAS ---
    def cambiar_vista(self, nueva_vista_clase):
        """Destruye la vista actual y carga un nuevo Frame en el contenedor."""
        if self.vista_actual:
            self.vista_actual.destroy()
            
        self.vista_actual = nueva_vista_clase(self.frame_contenido)
        self.vista_actual.pack(fill="both", expand=True, padx=20, pady=20)
        
    # --- MÉTODOS DE LOS BOTONES DEL MENÚ ---
    def mostrar_caja(self):
        """Pantalla predeterminada temporal"""
        if self.vista_actual:
            self.vista_actual.destroy()
            
        self.vista_actual = nuevo_label(self.frame_contenido, "Pantalla de Caja (En construcción)", fuente=FUENTE_TITULOS)
        self.vista_actual.pack(expand=True)

    def mostrar_agregar(self):
        self.cambiar_vista(VistaAgregarProducto)

    def mostrar_editar(self):
        self.cambiar_vista(VistaEditarProducto)