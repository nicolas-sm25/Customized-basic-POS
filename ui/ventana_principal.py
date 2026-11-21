import customtkinter as ctk
import tkinter.messagebox as messagebox

from PIL import Image

import os

from dal.conexion_DB import CARPETA_IMAGENES

from ui.componentes.creador_componentes import *

from ui.vistas.vista_agregar_productos import VistaAgregarProducto
from ui.vistas.vista_caja import VistaCaja
from ui.vistas.vista_editar_producto import VistaEditarProducto
from ui.vistas.vista_inventario import VistaInventario
from ui.vistas.vista_historial import VistaHistorial
from ui.vistas.vista_configuracion import VistaConfiguracion
from ui.vistas.vista_notificaciones import VistaNotificaciones
from ui.vistas.vista_proveedores import VistaProveedores

from ui.modales.modal_login import ModalLogin

from bll.gestor_caja import obtener_caja_abierta, verificar_cierre_inesperado
from bll.gestor_notificaciones import sincronizar_notificaciones_sistema, contar_notificaciones_activas
from bll.gestor_impresora import abrir_cajon_monedero

class VentanaPrincipal(ctk.CTk):
    def __init__(self, nombre_tienda= "TIENDA"):
        super().__init__()

        self.title(nombre_tienda)
        self.nombre_tienda_actual = nombre_tienda
        self.geometry("1000x600")
        self.after(0, lambda: self.state('zoomed'))
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.usuario_actual = None

        self.carrito_guardado = []
        self._ultimo_total_notificaciones = None
        self._timer_parpadeo_id = None
        self._estado_parpadeo = False
        self._alerta_no_vista = False

        # --- INTERCEPCIÓN DEL CIERRE DE WINDOWS ---
        self.protocol("WM_DELETE_WINDOW", self.intentar_cerrar_app)

        # --- MENÚ LATERAL (Oculto inicialmente hasta loguearse) ---
        self.frame_menu = nuevo_frame(self, color_fondo=None, radio_esquinas=0, ancho=200)
        self.frame_menu.grid(row=0, column=0, sticky="nsew")

        self.frame_contenido = nuevo_frame(self)
        self.frame_contenido.grid(row=0, column=1, sticky="nsew")
        self.vista_actual = None 

        verificar_cierre_inesperado()
        sincronizar_notificaciones_sistema(reiniciar_ignoradas=True)

        # Lanzar modal de login al abrir la app
        self.after(100, lambda: ModalLogin(self, self.iniciar_sesion_exitoso))

    def iniciar_sesion_exitoso(self, usuario):
        self.usuario_actual = usuario
        sincronizar_notificaciones_sistema(reiniciar_ignoradas=True)
        self.construir_menu()
        self.mostrar_caja()

    def construir_menu(self):
        for widget in self.frame_menu.winfo_children():
            widget.destroy()

        self.frame_menu.grid_rowconfigure(9, weight=1)
        self.frame_menu.grid_rowconfigure(10, weight=1)
        self.frame_menu.grid_rowconfigure(11, weight=1)

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
            
            self.btn_proveedores = nuevo_boton(self.frame_menu, "Proveedores", comando=self.mostrar_proveedores)
            self.btn_proveedores.grid(row=8, column=0, padx=20, pady=8)

        self.btn_abrir_cajon = nuevo_boton(
            self.frame_menu,
            "Abrir Cajón",
            comando=self.accion_abrir_cajon,
            color_fondo="#078d3a",
            color_hover="#054d20"
        )
        self.btn_abrir_cajon.grid(row=9, column=0, padx=20, pady=8)

        self.btn_notificaciones = nuevo_boton(
            self.frame_menu,
            "Notificaciones (0)",
            comando=self.mostrar_notificaciones,
            color_fondo="#cc1111",
            color_hover="#9e0d0d"
        )
        self.btn_notificaciones.grid(row=10, column=0, padx=20, pady=10)

        self.btn_config = nuevo_boton(
            self.frame_menu, "Configuración", 
            comando=self.mostrar_configuracion,
            color_fondo="#797777", color_hover="#646363"
        )
        self.btn_config.grid(row=11, column=0, padx=20, pady=15)
        self.actualizar_contador_notificaciones()
        self.actualizar_estado_boton_cajon()

    def cambiar_vista(self, nueva_vista_clase):

        if self.vista_actual and isinstance(self.vista_actual, VistaCaja) and hasattr(self.vista_actual, 'panel_carrito'):
            self.carrito_guardado = list(self.vista_actual.panel_carrito.items)

        if self.vista_actual:
            self.vista_actual.destroy()
            
        self.vista_actual = nueva_vista_clase(self.frame_contenido)
        self.vista_actual.pack(fill="both", expand=True, padx=20, pady=20)
        self.actualizar_contador_notificaciones()

    def mostrar_caja(self): self.cambiar_vista(VistaCaja)
    def mostrar_agregar(self): self.cambiar_vista(VistaAgregarProducto)
    def mostrar_editar(self, criterio_busqueda=None):
        self.cambiar_vista(VistaEditarProducto)
        if criterio_busqueda:
            self.after(10, lambda: self.vista_actual.buscar_externamente(criterio_busqueda))
    def mostrar_inventario(self): self.cambiar_vista(VistaInventario)
    def mostrar_historial(self): self.cambiar_vista(VistaHistorial)
    def mostrar_proveedores(self): self.cambiar_vista(VistaProveedores)
    
    def actualizar_estado_boton_cajon(self):
        """Habilita 'Abrir Cajón' si hay una caja abierta o si el usuario es Administrador."""
        if not hasattr(self, "btn_abrir_cajon") or not self.btn_abrir_cajon.winfo_exists():
            return
        es_admin = (self.usuario_actual or {}).get("rol") == "Administrador"
        hay_caja = obtener_caja_abierta() is not None
        if es_admin or hay_caja:
            self.btn_abrir_cajon.configure(state="normal", fg_color="#0bac49", hover_color="#054d20")
        else:
            self.btn_abrir_cajon.configure(state="disabled", fg_color="#3a3a3a")

    def accion_abrir_cajon(self):
        exito, msg = abrir_cajon_monedero(forzar_manual=True)
        if not exito:
            messagebox.showwarning("Cajón Monedero", msg)

    def mostrar_notificaciones(self):
        self._alerta_no_vista = False
        self.detener_parpadeo_notificaciones(quitar_borde=True)
        self.cambiar_vista(VistaNotificaciones)

    def actualizar_contador_notificaciones(self):
        if not hasattr(self, "btn_notificaciones") or not self.btn_notificaciones.winfo_exists():
            return

        total = contar_notificaciones_activas()
        anterior = self._ultimo_total_notificaciones
        self._ultimo_total_notificaciones = total

        if total == 0:
            self._alerta_no_vista = False
            self.detener_parpadeo_notificaciones(quitar_borde=True)
            self.btn_notificaciones.configure(
                text="Notificaciones (0)",
                fg_color="#444444",
                hover_color="#5a5a5a",
                text_color="#ffffff",
                border_width=0
            )
            return

        self.btn_notificaciones.configure(text=f"Notificaciones ({total})")

        if anterior is None or total > anterior:
            if isinstance(self.vista_actual, VistaNotificaciones):
                self._alerta_no_vista = False
            else:
                self._alerta_no_vista = True
                self.iniciar_parpadeo_notificaciones(ciclos=32)
                return

        if self._timer_parpadeo_id is None:
            self.btn_notificaciones.configure(
                fg_color="#cc1111",
                hover_color="#9e0d0d",
                text_color="#ffffff",
                border_width=2 if self._alerta_no_vista else 0,
                border_color="#f39c12"
            )

    def iniciar_parpadeo_notificaciones(self, ciclos=16):
        """Alterna el color y borde del botón de notificaciones para llamar la atención del cajero."""
        self.detener_parpadeo_notificaciones(quitar_borde=False)
        self._estado_parpadeo = False
        self._tick_parpadeo_notificaciones(ciclos)

    def _tick_parpadeo_notificaciones(self, ciclos_restantes):
        if not hasattr(self, "btn_notificaciones") or not self.btn_notificaciones.winfo_exists():
            self._timer_parpadeo_id = None
            return

        total = self._ultimo_total_notificaciones or 0
        if total == 0:
            self.detener_parpadeo_notificaciones(quitar_borde=True)
            return

        if ciclos_restantes <= 0:
            self._timer_parpadeo_id = None
            self.btn_notificaciones.configure(
                text=f"Notificaciones ({total})",
                fg_color="#cc1111",
                hover_color="#9e0d0d",
                text_color="#ffffff",
                border_width=2 if self._alerta_no_vista else 0,
                border_color="#f39c12"
            )
            return

        self._estado_parpadeo = not self._estado_parpadeo
        if self._estado_parpadeo:
            self.btn_notificaciones.configure(
                text=f"Notificaciones ({total})",
                fg_color="#f39c12",
                hover_color="#d68910",
                text_color="#111111",
                border_width=2,
                border_color="#ffffff"
            )
        else:
            self.btn_notificaciones.configure(
                text=f"Notificaciones ({total})",
                fg_color="#e53935",
                hover_color="#b71c1c",
                text_color="#ffffff",
                border_width=2,
                border_color="#f39c12"
            )

        self._timer_parpadeo_id = self.after(
            420,
            lambda: self._tick_parpadeo_notificaciones(ciclos_restantes - 1)
        )

    def detener_parpadeo_notificaciones(self, quitar_borde=True):
        if self._timer_parpadeo_id is not None:
            try:
                self.after_cancel(self._timer_parpadeo_id)
            except Exception:
                pass
            self._timer_parpadeo_id = None

        if hasattr(self, "btn_notificaciones") and self.btn_notificaciones.winfo_exists():
            total = self._ultimo_total_notificaciones or 0
            mantener_borde = (not quitar_borde) and self._alerta_no_vista and total > 0
            self.btn_notificaciones.configure(
                text=f"Notificaciones ({total})" if total > 0 else "Notificaciones (0)",
                fg_color="#cc1111" if total > 0 else "#444444",
                hover_color="#9e0d0d" if total > 0 else "#5a5a5a",
                text_color="#ffffff",
                border_width=2 if mantener_borde else 0,
                border_color="#f39c12"
            )

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