import json
import os
import shutil
from tkinter import filedialog
import customtkinter as ctk
from ui.componentes.configuracion_componentes import ConfiguracionComponentes
from ui.componentes.creador_componentes import *
from ui.modales.modal_usuarios import ModalUsuarios
from dal.conexion_DB import SessionLocal, CARPETA_CONFIG, CARPETA_IMAGENES
from dal.modelos.usuarios import Usuario

class VistaConfiguracion(ConfiguracionComponentes):
    def __init__(self, master, callback_cerrar_sesion):
        super().__init__(master)
        self.callback_cerrar_sesion = callback_cerrar_sesion

        self.config_path = os.path.join(CARPETA_CONFIG, "config.json")

        # --- TÍTULO ---
        self.lbl_titulo = nuevo_label(self, "Configuración del Sistema", fuente=FUENTE_TITULOS)
        self.lbl_titulo.pack(pady=15)

        # --- CONTENEDOR PRINCIPAL ---
        self.frame_container = nuevo_frame(self, color_fondo="#202020", radio_esquinas=10)
        self.frame_container.pack(fill="both", expand=True, padx=20, pady=10)

        f_contenido = ctk.CTkScrollableFrame(self.frame_container, fg_color="transparent")
        f_contenido.pack(fill="both", expand=True, padx=20, pady=20)

        # --- SECCIÓN: CUENTA Y SESIÓN ---
        nuevo_label(f_contenido, "Control de Sesión", fuente=("Arial", 16, "bold"), color_texto="#d4ac0d", poscicion="w").pack(anchor="w", pady=(25, 10))

        f_sesion = nuevo_frame(f_contenido, color_fondo="#2b2b2b")
        f_sesion.pack(fill="x", pady=5, padx=5)

        f_info_sesion = nuevo_frame(f_sesion, color_fondo="transparent")
        f_info_sesion.pack(side="left", padx=15, pady=15)
        nuevo_label(f_info_sesion, "Cerrar sesión actual", fuente=("Arial", 13, "bold"), poscicion="w").pack(anchor="w")
        nuevo_label(f_info_sesion, "Volverás a la pantalla de inicio de sesión.", fuente=("Arial", 11), color_texto="#a0a0a0", poscicion="w").pack(anchor="w")

        nuevo_boton(
            f_sesion, 
            "Cerrar Sesión", 
            comando=self.callback_cerrar_sesion, 
            color_fondo=COLOR_FALLO, 
            color_hover=COLOR_FALLO_HOVER,
            ancho=140
        ).pack(side="right", padx=15, pady=15)

        # --- SECCIÓN: CREAR USUARIO NUEVO ---
        rol_usuario = self.winfo_toplevel().usuario_actual['rol']

        nuevo_label(f_contenido, "Gestión de Usuarios", fuente=("Arial", 16, "bold"), color_texto="#d4ac0d", poscicion="w").pack(anchor="w", pady=(25, 10))
        f_crear = nuevo_frame(f_contenido, color_fondo="#2b2b2b")
        f_crear.pack(fill="x", pady=5, padx=5)

        if rol_usuario == "Administrador":

            f_form_container = nuevo_frame(f_crear, color_fondo="transparent")
            f_form_container.pack(fill="x", padx=15, pady=15)

            f_form = nuevo_frame(f_form_container, color_fondo="transparent", ancho=350)
            f_form.pack(expand=True, pady=10)

            self.entry_nombre = nueva_caja_texto(f_form, placeholder="Nombre completo")
            self.entry_nombre.configure(width=350, justify="left")
            self.entry_nombre.pack(pady=5)
            
            self.entry_username = nueva_caja_texto(f_form, placeholder="Usuario (Login)")
            self.entry_username.configure(width=350,justify="left")
            self.entry_username.pack(pady=5)
            
            self.entry_password = nueva_caja_texto(f_form, placeholder="Contraseña")
            self.entry_password.configure(show="*", width=350, justify="left")
            self.entry_password.pack(pady=5)

            f_rol = nuevo_frame(f_form, color_fondo="transparent")
            f_rol.pack(fill="x", pady=5)
            nuevo_label(f_rol, "Rol del usuario:", fuente=("Arial", 12), poscicion="w").pack(side="left")
            
            self.combo_rol = ctk.CTkOptionMenu(f_rol, values=["Vendedor", "Administrador"], fg_color="#3b3b3b", button_color="#4b4b4b", button_hover_color="#5b5b5b", width=140)
            self.combo_rol.pack(side="right")
            self.combo_rol.set("Vendedor")

            self.lbl_mensaje_usuario = nuevo_label(f_form, "", color_texto=COLOR_EXITO)
            self.lbl_mensaje_usuario.pack(pady=5)

            f_botones = nuevo_frame(f_form, color_fondo="transparent")
            f_botones.pack(fill="x", pady=(5, 0))
            
            nuevo_boton(f_botones, "Registrar Nuevo", comando=self.registrar_usuario_desde_ui, color_fondo=COLOR_EXITO, color_hover=COLOR_EXITO_HOVER).pack(side="left", fill="x", expand=True, padx=2)
            nuevo_boton(f_botones, "Ver Usuarios Registrados", comando=lambda: ModalUsuarios(self), color_fondo="#3498db", color_hover="#2980b9").pack(side="right", fill="x", expand=True, padx=2)
        else:
            nuevo_label(f_crear, "🔒 Acceso restringido.\nSolo los administradores pueden crear o ver usuarios.", fuente=("Arial", 13), color_texto=COLOR_FALLO).pack(pady=30)

        # --- SECCIÓN: PERSONALIZACIÓN DE TIENDA ---
        nuevo_label(f_contenido, "Personalización de la Tienda", fuente=("Arial", 16, "bold"), color_texto="#d4ac0d", poscicion="w").pack(anchor="w", pady=(25, 10))
        
        f_tienda = nuevo_frame(f_contenido, color_fondo="#2b2b2b")
        f_tienda.pack(fill="x", pady=5, padx=5)

        if rol_usuario == "Administrador":
            
            # Cambiar Nombre
            f_nombre = nuevo_frame(f_tienda, color_fondo="transparent")
            f_nombre.pack(fill="x", pady=10)
            nuevo_label(f_nombre, "Nombre de la Tienda:", fuente=("Arial", 13), poscicion="w").pack(side="left", padx=15)
            
            self.entry_nombre_tienda = nueva_caja_texto(f_nombre, placeholder="Ej: Mi Tienda")
            self.entry_nombre_tienda.pack(side="left", padx=10, fill="x", expand=True)
            nombre_actual = self.winfo_toplevel().nombre_tienda_actual
            self.entry_nombre_tienda.insert(0, nombre_actual)
            
            btn_guardar_nombre = nuevo_boton(f_nombre, "Actualizar", comando=self.guardar_nombre_tienda, ancho=100)
            btn_guardar_nombre.pack(side="right", padx=15)
            
            # --- IMPORTAR IMÁGENES MEDIANTE INTERFAZ ---
            f_logo = nuevo_frame(f_tienda, color_fondo="#1c1c1c", radio_esquinas=8)
            f_logo.pack(pady=15, padx=30, fill="none")

            nuevo_label(
                f_logo, 
                "Identidad Visual (Requiere reiniciar el programa para aplicar los cambios):", 
                fuente=("Arial", 12, "bold"), 
                color_texto="#a0a0a0", 
                poscicion="w"
            ).pack(anchor="w", padx=15, pady=(12, 8))

            f_botones_img = nuevo_frame(f_logo, color_fondo="transparent")
            f_botones_img.pack(pady=(0, 12), padx=15)

            btn_importar_icono = nuevo_boton(
                f_botones_img, 
                "Importar Ícono (.ico)", 
                comando=self.importar_icono, 
                color_fondo="#3498db", 
                color_hover="#2980b9",
                ancho=160
            )
            btn_importar_icono.pack(side="left", padx=8)

            btn_importar_logo = nuevo_boton(
                f_botones_img, 
                "Importar Logo Menú (.png)", 
                comando=self.importar_logo, 
                color_fondo="#5e17eb", 
                color_hover="#4a11c0",
                ancho=180
            )
            btn_importar_logo.pack(side="left", padx=8)

            self.lbl_mensaje_img = nuevo_label(f_logo, "", color_texto=COLOR_EXITO)
            self.lbl_mensaje_img.pack(pady=(0, 8))

        else:
            nuevo_label(f_tienda, "🔒 Acceso restringido.\nSolo los administradores pueden editar nombre y logo.", fuente=("Arial", 13), color_texto=COLOR_FALLO).pack(pady=30)

    def cambiar_tema(self, nuevo_modo):
        ctk.set_appearance_mode(nuevo_modo)

    def registrar_usuario_desde_ui(self):
        nombre = self.entry_nombre.get().strip()
        username = self.entry_username.get().strip()
        password = self.entry_password.get().strip()
        rol = self.combo_rol.get()

        if not nombre or not username or not password:
            self.lbl_mensaje_usuario.configure(text="Todos los campos son obligatorios.", text_color=COLOR_FALLO)
            return

        sesion = SessionLocal()
        try:
            existente = sesion.query(Usuario).filter(Usuario.username == username).first()
            if existente:
                self.lbl_mensaje_usuario.configure(text="El usuario ya existe.", text_color=COLOR_FALLO)
                return

            nuevo_u = Usuario(nombre=nombre, username=username, password=password, rol=rol)
            sesion.add(nuevo_u)
            sesion.commit()

            self.lbl_mensaje_usuario.configure(text=f"¡Usuario '{username}' creado con éxito!", text_color=COLOR_EXITO)
            self.entry_nombre.delete(0, 'end')
            self.entry_username.delete(0, 'end')
            self.entry_password.delete(0, 'end')
        except Exception as e:
            sesion.rollback()
            self.lbl_mensaje_usuario.configure(text=f"Error al registrar: {str(e)}", text_color=COLOR_FALLO)
        finally:
            sesion.close()

    def guardar_nombre_tienda(self):
        nuevo_nombre = self.entry_nombre_tienda.get().strip()
        if not nuevo_nombre: return
        
        cfg = {}
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                try: cfg = json.load(f)
                except: pass
        
        cfg["nombre_tienda"] = nuevo_nombre
        
        with open(self.config_path, 'w') as f:
            json.dump(cfg, f)

        ventana = self.winfo_toplevel()
        ventana.title(nuevo_nombre)
        ventana.nombre_tienda_actual = nuevo_nombre
        if hasattr(ventana, 'lbl_nombre_tienda'):
            ventana.lbl_nombre_tienda.configure(text=nuevo_nombre)

        self.entry_nombre_tienda.configure(text_color=COLOR_EXITO)
        self.after(2000, lambda: self.entry_nombre_tienda.configure(text_color="white"))

    def importar_icono(self):
        ruta_origen = filedialog.askopenfilename(
            title="Seleccionar Ícono de la Ventana",
            filetypes=[("Archivos de Ícono", "*.ico")]
        )
        if ruta_origen:
            self.guardar_imagen_en_datos(ruta_origen, ".ico", "Ícono")

    def importar_logo(self):
        ruta_origen = filedialog.askopenfilename(
            title="Seleccionar Logo del Menú",
            filetypes=[("Imágenes PNG", "*.png")]
        )
        if ruta_origen:
            self.guardar_imagen_en_datos(ruta_origen, ".png", "Logo")

    def guardar_imagen_en_datos(self, ruta_origen, extension, tipo):
        try:
            for archivo in os.listdir(CARPETA_IMAGENES):
                if archivo.lower().endswith(extension):
                    os.remove(os.path.join(CARPETA_IMAGENES, archivo))

            nombre_archivo = os.path.basename(ruta_origen)
            ruta_destino = os.path.join(CARPETA_IMAGENES, nombre_archivo)
            shutil.copy2(ruta_origen, ruta_destino)
            
            self.lbl_mensaje_img.configure(text=f"¡{tipo} importado con éxito!", text_color=COLOR_EXITO)
            self.after(3000, lambda: self.lbl_mensaje_img.configure(text=""))
        except Exception as e:
            self.lbl_mensaje_img.configure(text=f"Error al importar: {e}", text_color=COLOR_FALLO)