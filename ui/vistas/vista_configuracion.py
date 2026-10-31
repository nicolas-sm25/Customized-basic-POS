import customtkinter as ctk
from ui.componentes.configuracion_componentes import ConfiguracionComponentes
from ui.componentes.creador_componentes import *
from dal.conexion_DB import SessionLocal
from dal.modelos.usuarios import Usuario

class VistaConfiguracion(ConfiguracionComponentes):
    def __init__(self, master, callback_cerrar_sesion):
        super().__init__(master)
        self.callback_cerrar_sesion = callback_cerrar_sesion

        # --- TÍTULO ---
        self.lbl_titulo = nuevo_label(self, "Configuración del Sistema", fuente=FUENTE_TITULOS)
        self.lbl_titulo.pack(pady=15)

        # --- CONTENEDOR PRINCIPAL ---
        self.frame_container = nuevo_frame(self, color_fondo="#202020", radio_esquinas=10)
        self.frame_container.pack(fill="both", expand=True, padx=20, pady=10)

        f_contenido = ctk.CTkScrollableFrame(self.frame_container, fg_color="transparent")
        f_contenido.pack(fill="both", expand=True, padx=20, pady=20)

        # --- SECCIÓN: APARIENCIA ---
        nuevo_label(f_contenido, "Apariencia de la Interfaz", fuente=("Arial", 16, "bold"), color_texto="#d4ac0d", poscicion="w").pack(anchor="w", pady=(0, 10))
        
        f_tema = nuevo_frame(f_contenido, color_fondo="#2b2b2b")
        f_tema.pack(fill="x", pady=5, padx=5)
        
        nuevo_label(f_tema, "Tema visual:", fuente=("Arial", 13), poscicion="w").pack(side="left", padx=15, pady=15)
        
        self.combo_tema = ctk.CTkOptionMenu(
            f_tema, 
            values=["Dark", "Light", "System"],
            command=self.cambiar_tema,
            fg_color="#3b3b3b",
            button_color="#4b4b4b",
            button_hover_color="#5b5b5b",
            width=140
        )
        self.combo_tema.pack(side="right", padx=15, pady=15)
        self.combo_tema.set(ctk.get_appearance_mode())

        # --- SECCIÓN: CREAR USUARIO NUEVO ---
        nuevo_label(f_contenido, "Gestión de Usuarios (Crear Nuevo)", fuente=("Arial", 16, "bold"), color_texto="#d4ac0d", poscicion="w").pack(anchor="w", pady=(25, 10))
        
        f_crear = nuevo_frame(f_contenido, color_fondo="#2b2b2b")
        f_crear.pack(fill="x", pady=5, padx=5)

        f_form = nuevo_frame(f_crear, color_fondo="transparent")
        f_form.pack(fill="x", padx=15, pady=15)

        self.entry_nombre = nueva_caja_texto(f_form, placeholder="Nombre completo")
        self.entry_nombre.pack(fill="x", pady=5)

        self.entry_username = nueva_caja_texto(f_form, placeholder="Usuario (Login)")
        self.entry_username.pack(fill="x", pady=5)

        self.entry_password = nueva_caja_texto(f_form, placeholder="Contraseña")
        self.entry_password.configure(show="*")
        self.entry_password.pack(fill="x", pady=5)

        # Menú desplegable para el Rol
        f_rol = nuevo_frame(f_form, color_fondo="transparent")
        f_rol.pack(fill="x", pady=5)
        nuevo_label(f_rol, "Rol del usuario:", fuente=("Arial", 12), poscicion="w").pack(side="left")
        
        self.combo_rol = ctk.CTkOptionMenu(
            f_rol,
            values=["Vendedor", "Administrador"],
            fg_color="#3b3b3b",
            button_color="#4b4b4b",
            button_hover_color="#5b5b5b",
            width=140
        )
        self.combo_rol.pack(side="right")
        self.combo_rol.set("Vendedor")

        self.lbl_mensaje_usuario = nuevo_label(f_form, "", color_texto=COLOR_EXITO)
        self.lbl_mensaje_usuario.pack(pady=5)

        nuevo_boton(
            f_form,
            "Registrar Usuario",
            comando=self.registrar_usuario_desde_ui,
            color_fondo=COLOR_EXITO,
            color_hover=COLOR_EXITO_HOVER
        ).pack(fill="x", ipady=5, pady=(5, 0))

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