import customtkinter as ctk
from ui.componentes.creador_componentes import *
from ui.vistas.vista_agregar_productos import VistaAgregarProducto
from ui.vistas.vista_caja import VistaCaja
from ui.vistas.vista_editar_producto import VistaEditarProducto
from ui.vistas.vista_inventario import VistaInventario
from ui.vistas.vista_historial import VistaHistorial
from ui.modales.modal_login import ModalLogin
from ui.vistas.vista_configuracion import VistaConfiguracion

class VentanaPrincipal(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Sistema POS - Mi Tienda")
        self.geometry("950x650")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        self.usuario_actual = None

        # --- MENÚ LATERAL (Oculto inicialmente hasta loguearse) ---
        self.frame_menu = nuevo_frame(self, color_fondo=None, radio_esquinas=0, ancho=200)
        self.frame_menu.grid(row=0, column=0, sticky="nsew")
        
        self.frame_contenido = nuevo_frame(self)
        self.frame_contenido.grid(row=0, column=1, sticky="nsew")
        self.vista_actual = None 

        # Lanzar modal de login al abrir la app
        self.after(100, lambda: ModalLogin(self, self.iniciar_sesion_exitoso))

    def iniciar_sesion_exitoso(self, usuario):
        self.usuario_actual = usuario
        self.construir_menu()
        self.mostrar_caja()

    def construir_menu(self):
        for widget in self.frame_menu.winfo_children():
            widget.destroy()

        self.frame_menu.grid_rowconfigure(8, weight=1)

        self.lbl_logo = nuevo_label(self.frame_menu, "TIENDA", fuente=FUENTE_TITULOS)
        self.lbl_logo.grid(row=0, column=0, padx=20, pady=20)

        # Info del usuario conectado
        nuevo_label(self.frame_menu, f"User: {self.usuario_actual['nombre']}\nRol: {self.usuario_actual['rol']}", fuente=("Arial", 11), color_texto="#d4ac0d").grid(row=1, column=0, padx=20, pady=(0, 15))

        # 1. Caja (Disponible para todos)
        self.btn_caja = nuevo_boton(self.frame_menu, "Caja", comando=self.mostrar_caja)
        self.btn_caja.grid(row=2, column=0, padx=20, pady=8)

        # 2. Inventario (Disponible para todos, pero evaluaremos el rol de edición dentro de la vista si es necesario)
        self.btn_inventario = nuevo_boton(self.frame_menu, "Inventario", comando=self.mostrar_inventario)
        self.btn_inventario.grid(row=3, column=0, padx=20, pady=8)

        # Si es Administrador, mostramos las funciones gerenciales y de gestión
        if self.usuario_actual['rol'] == "Administrador":
            self.btn_agregar = nuevo_boton(self.frame_menu, "Agregar Producto", comando=self.mostrar_agregar)
            self.btn_agregar.grid(row=4, column=0, padx=20, pady=8)
            
            self.btn_editar = nuevo_boton(self.frame_menu, "Editar Producto", comando=self.mostrar_editar)
            self.btn_editar.grid(row=5, column=0, padx=20, pady=8)
            
            self.btn_historial = nuevo_boton(self.frame_menu, "Historial", comando=self.mostrar_historial)
            self.btn_historial.grid(row=6, column=0, padx=20, pady=8)
        
        self.btn_config = nuevo_boton(self.frame_menu, "Configuración", 
        comando=self.mostrar_configuracion,color_fondo="#3b3b3b", color_hover="#555555")
        self.btn_config.grid(row=8, column=0, padx=20, pady=15)

    def cambiar_vista(self, nueva_vista_clase):
        if self.vista_actual:
            self.vista_actual.destroy()
        self.vista_actual = nueva_vista_clase(self.frame_contenido)
        self.vista_actual.pack(fill="both", expand=True, padx=20, pady=20)

    def mostrar_caja(self): self.cambiar_vista(VistaCaja)
    def mostrar_agregar(self): self.cambiar_vista(VistaAgregarProducto)
    def mostrar_editar(self): self.cambiar_vista(VistaEditarProducto)
    def mostrar_inventario(self): self.cambiar_vista(VistaInventario)
    def mostrar_historial(self): self.cambiar_vista(VistaHistorial)
    
    # --- MENÚ CONFIGURACIÓN ---
    def mostrar_configuracion(self):
        if self.vista_actual:
            self.vista_actual.destroy()
        self.vista_actual = VistaConfiguracion(self.frame_contenido, self.cerrar_sesion)
        self.vista_actual.pack(fill="both", expand=True, padx=20, pady=20)

    def cerrar_sesion(self):
        if self.vista_actual:
            self.vista_actual.destroy()
            self.vista_actual = None
        for widget in self.frame_menu.winfo_children():
            widget.destroy()
        ModalLogin(self, self.iniciar_sesion_exitoso)