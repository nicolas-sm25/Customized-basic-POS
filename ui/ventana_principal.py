import customtkinter as ctk
import tkinter.messagebox as messagebox

from PIL import Image, ImageTk

import os

from dal.conexion_DB import CARPETA_IMAGENES

from ui.componentes.creador_componentes import *

from ui.vistas.vista_agregar_productos import VistaAgregarProducto
from ui.vistas.vista_caja import VistaCaja
from ui.vistas.vista_editar_producto import VistaEditarProducto
from ui.vistas.vista_inventario import VistaInventario
from ui.vistas.vista_historial import VistaHistorial
from ui.vistas.vista_configuracion import VistaConfiguracion

from ui.modales.modal_login import ModalLogin

from bll.gestor_caja import obtener_caja_abierta

class VentanaPrincipal(ctk.CTk):
    def __init__(self, nombre_tienda= "TIENDA"):
        super().__init__()
        
        self.title(nombre_tienda)
        self.nombre_tienda_actual = nombre_tienda
        self.geometry("950x650")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        self.usuario_actual = None

        # --- INTERCEPCIÓN DEL CIERRE DE WINDOWS ---
        self.protocol("WM_DELETE_WINDOW", self.intentar_cerrar_app)

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

        try:
            pngs = [f for f in os.listdir(CARPETA_IMAGENES) if f.lower().endswith('.png')]
            
            if pngs:
                ruta_logo_png = os.path.join(CARPETA_IMAGENES, pngs[0])
                img = Image.open(ruta_logo_png)
                img = img.resize((120, 120), Image.Resampling.LANCZOS) 
                logo_ctk = ctk.CTkImage(light_image=img, dark_image=img, size=(120,120))
                
                self.lbl_imagen = ctk.CTkLabel(self.frame_menu, text="", image=logo_ctk)
                self.lbl_imagen.image = logo_ctk
                self.lbl_imagen.grid(row=0, column=0, padx=20, pady=(20, 5))
                
                self.lbl_nombre_tienda = nuevo_label(self.frame_menu, self.nombre_tienda_actual, fuente=("Arial", 16, "bold"))
                self.lbl_nombre_tienda.grid(row=1, column=0, padx=20, pady=(0,15))
            else:
                self.lbl_nombre_tienda = nuevo_label(self.frame_menu, self.nombre_tienda_actual, fuente=FUENTE_TITULOS)
                self.lbl_nombre_tienda.grid(row=0, column=0, padx=20, pady=20)
                
        except Exception as e:
            self.lbl_nombre_tienda = nuevo_label(self.frame_menu, self.nombre_tienda_actual, fuente=FUENTE_TITULOS)
            self.lbl_nombre_tienda.grid(row=0, column=0, padx=20, pady=20)
            import logging
            logging.error(f"Error cargando imagen logo menu: {e}")

        # Info del usuario conectado
        frame_user = nuevo_frame(self.frame_menu)
        frame_user.grid(row=2, column=0, padx=20, pady=(0, 15))
        nuevo_label(frame_user, f"{self.usuario_actual['nombre']}", fuente=("Arial", 14, "bold"), color_texto="#ffffff").pack()
        nuevo_label(frame_user, f"{self.usuario_actual['rol']}", fuente=("Arial", 12), color_texto="#d4ac0d").pack()

        # 1. Caja (Disponible para todos)
        self.btn_caja = nuevo_boton(self.frame_menu, "Caja", comando=self.mostrar_caja)
        self.btn_caja.grid(row=3, column=0, padx=20, pady=8)

        # 2. Inventario 
        self.btn_inventario = nuevo_boton(self.frame_menu, "Inventario", comando=self.mostrar_inventario)
        self.btn_inventario.grid(row=4, column=0, padx=20, pady=8)

        # Si es Administrador, mostramos las funciones gerenciales
        if self.usuario_actual['rol'] == "Administrador":
            self.btn_agregar = nuevo_boton(self.frame_menu, "Agregar Producto", comando=self.mostrar_agregar)
            self.btn_agregar.grid(row=5, column=0, padx=20, pady=8)
            
            self.btn_editar = nuevo_boton(self.frame_menu, "Editar Producto", comando=self.mostrar_editar)
            self.btn_editar.grid(row=6, column=0, padx=20, pady=8)
            
            self.btn_historial = nuevo_boton(self.frame_menu, "Historial", comando=self.mostrar_historial)
            self.btn_historial.grid(row=7, column=0, padx=20, pady=8)
        
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
    def mostrar_editar(self, criterio_busqueda=None):
        self.cambiar_vista(VistaEditarProducto)
        if criterio_busqueda:
            self.after(10, lambda: self.vista_actual.buscar_externamente(criterio_busqueda))
    def mostrar_inventario(self): self.cambiar_vista(VistaInventario)
    def mostrar_historial(self): self.cambiar_vista(VistaHistorial)
    
    # --- MENÚ CONFIGURACIÓN ---
    def mostrar_configuracion(self):
        if self.vista_actual:
            self.vista_actual.destroy()
        self.vista_actual = VistaConfiguracion(self.frame_contenido, self.cerrar_sesion)
        self.vista_actual.pack(fill="both", expand=True, padx=20, pady=20)

    # --- LÓGICA DE BLOQUEO DE CIERRE ---
    def intentar_cerrar_app(self):
        """Se ejecuta cuando el usuario le da a la X roja de la ventana."""
        if obtener_caja_abierta():
            messagebox.showwarning("Cierre Denegado", "Debes hacer el Cierre de Caja antes de salir del programa.")
            return 
        self.destroy()

    def cerrar_sesion(self):
        """Se ejecuta desde el botón de cerrar sesión en Configuración."""
        if obtener_caja_abierta():
            messagebox.showwarning("Cierre Denegado", "Debes hacer el Cierre de Caja antes de cerrar sesión.")
            return 

        if self.vista_actual:
            self.vista_actual.destroy()
            self.vista_actual = None
        for widget in self.frame_menu.winfo_children():
            widget.destroy()
        ModalLogin(self, self.iniciar_sesion_exitoso)