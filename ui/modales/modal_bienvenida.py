import json
import os
import customtkinter as ctk
from ui.componentes.creador_componentes import *
from dal.conexion_DB import CARPETA_CONFIG
from bll.gestor_usuarios import crear_usuario


class ModalBienvenidaAdmin(ctk.CTkToplevel):
    def __init__(self, master, callback_exito):
        super().__init__(master)
        self.callback_exito = callback_exito
        self.config_path = os.path.join(CARPETA_CONFIG, "config.json")

        self.title("Configuración Inicial del Sistema")
        ancho_win = 560
        alto_win = 660
        self.geometry(f"{ancho_win}x{alto_win}")
        self.resizable(False, False)
        self.configure(fg_color="#1e1e1e")

        self.transient(master)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.cerrar_aplicacion)

        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (ancho_win // 2)
        y = (self.winfo_screenheight() // 2) - (alto_win // 2)
        self.geometry(f"+{x}+{y}")

        # --- CABECERA ---
        f_header = nuevo_frame(self, color_fondo="transparent")
        f_header.pack(fill="x", padx=30, pady=(24, 12))

        nuevo_label(
            f_header,
            "Tu negocio al siguiente nivel",
            fuente=("Arial", 24, "bold"),
            color_texto="#d4ac0d"
        ).pack(pady=(0, 6))

        nuevo_label(
            f_header,
            "Personaliza el nombre de tu negocio y crea la cuenta del\nAdministrador principal para tomar el control de tu tienda.",
            fuente=("Arial", 13),
            color_texto="#cccccc"
        ).pack()

        # --- BOTÓN INFERIOR ANCLADO ---
        f_footer = nuevo_frame(self, color_fondo="transparent")
        f_footer.pack(side="bottom", fill="x", padx=30, pady=(8, 22))

        self.lbl_error = nuevo_label(f_footer, "", fuente=("Arial", 12, "bold"), color_texto=COLOR_FALLO)
        self.lbl_error.pack(pady=(0, 8))

        self.btn_comenzar = nuevo_boton(
            f_footer,
            "Comenzar a Gestionar mi Negocio",
            comando=self.crear_admin_principal,
            color_fondo=COLOR_EXITO,
            color_hover=COLOR_EXITO_HOVER
        )
        self.btn_comenzar.configure(font=("Arial", 14, "bold"))
        self.btn_comenzar.pack(fill="x", ipady=8)

        # --- FORMULARIO CENTRAL ---
        f_form = nuevo_frame(self, color_fondo="#2b2b2b", radio_esquinas=12)
        f_form.pack(fill="both", expand=True, padx=30, pady=(4, 6))

        nuevo_label(f_form, "Nombre de la Tienda:", fuente=("Arial", 13, "bold"), poscicion="w").pack(anchor="w", padx=24, pady=(18, 4))
        self.entry_tienda = nueva_caja_texto(f_form, placeholder="")
        self.entry_tienda.configure(justify="left")
        self.entry_tienda.pack(fill="x", padx=24, pady=(0, 10))
        nombre_actual = getattr(master, "nombre_tienda_actual", "")
        if nombre_actual and nombre_actual != "TIENDA":
            self.entry_tienda.insert(0, nombre_actual)

        nuevo_label(f_form, "Nombre del Administrador:", fuente=("Arial", 13, "bold"), poscicion="w").pack(anchor="w", padx=24, pady=(4, 4))
        self.entry_nombre = nueva_caja_texto(f_form, placeholder="")
        self.entry_nombre.configure(justify="left")
        self.entry_nombre.pack(fill="x", padx=24, pady=(0, 10))

        nuevo_label(f_form, "Usuario de acceso (Login):", fuente=("Arial", 13, "bold"), poscicion="w").pack(anchor="w", padx=24, pady=(4, 4))
        self.entry_username = nueva_caja_texto(f_form, placeholder="")
        self.entry_username.configure(justify="left")
        self.entry_username.pack(fill="x", padx=24, pady=(0, 10))

        nuevo_label(f_form, "Contraseña:", fuente=("Arial", 13, "bold"), poscicion="w").pack(anchor="w", padx=24, pady=(4, 4))
        self.entry_password = nueva_caja_texto(f_form, placeholder="")
        self.entry_password.configure(show="*", justify="left")
        self.entry_password.pack(fill="x", padx=24, pady=(0, 10))

        nuevo_label(f_form, "Confirmar Contraseña:", fuente=("Arial", 13, "bold"), poscicion="w").pack(anchor="w", padx=24, pady=(4, 4))
        self.entry_confirmar = nueva_caja_texto(f_form, placeholder="")
        self.entry_confirmar.configure(show="*", justify="left")
        self.entry_confirmar.pack(fill="x", padx=24, pady=(0, 16))

        self.after(50, self.entry_tienda.focus)

    def cerrar_aplicacion(self):
        self.master.destroy()

    def crear_admin_principal(self):
        nombre_tienda = self.entry_tienda.get().strip() or "TIENDA"
        nombre = self.entry_nombre.get().strip()
        username = self.entry_username.get().strip()
        password = self.entry_password.get().strip()
        confirmar = self.entry_confirmar.get().strip()

        if not nombre or not username or not password:
            self.lbl_error.configure(text="Completa nombre, usuario y contraseña.")
            return

        if len(password) < 4:
            self.lbl_error.configure(text="La contraseña debe tener al menos 4 caracteres.")
            return

        if password != confirmar:
            self.lbl_error.configure(text="Las contraseñas no coinciden.")
            return

        exito, resultado = crear_usuario(nombre, username, password, rol="Administrador")
        if not exito:
            self.lbl_error.configure(text=resultado)
            return

        try:
            cfg = {}
            if os.path.exists(self.config_path):
                with open(self.config_path, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
            cfg["nombre_tienda"] = nombre_tienda
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(cfg, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

        self.master.title(nombre_tienda)
        self.master.nombre_tienda_actual = nombre_tienda

        self.grab_release()
        self.destroy()
        self.callback_exito(resultado)