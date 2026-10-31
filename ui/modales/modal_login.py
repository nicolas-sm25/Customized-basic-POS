import customtkinter as ctk
from ui.componentes.creador_componentes import *
from bll.gestor_usuarios import verificar_credenciales, inicializar_usuario_admin

class ModalLogin:
    def __init__(self, master, callback_exito):
        inicializar_usuario_admin()
        self.master = master
        self.modal = nuevo_modal(master, "Iniciar Sesión - Sistema POS", 400, 320)
        self.callback_exito = callback_exito

        frame_modal = nuevo_frame(self.modal)
        frame_modal.pack(expand=True, fill="both", padx=20, pady=20)

        nuevo_label(frame_modal, "Acceso al Sistema", fuente=FUENTE_TITULOS).pack(pady=10)

        self.entry_user = nueva_caja_texto(frame_modal, placeholder="Usuario")
        self.entry_user.pack(pady=8, fill="x", padx=20)

        self.entry_pass = nueva_caja_texto(frame_modal, placeholder="Contraseña")
        self.entry_pass.configure(show="*")
        self.entry_pass.pack(pady=8, fill="x", padx=20)

        self.lbl_error = nuevo_label(frame_modal, "", color_texto=COLOR_FALLO)
        self.lbl_error.pack(pady=5)

        frame_botones = nuevo_frame(frame_modal, color_fondo="transparent")
        frame_botones.pack(pady=10)

        nuevo_boton(frame_botones, "Ingresar (Enter)", comando=self.intentar_login, color_fondo=COLOR_EXITO, color_hover=COLOR_EXITO_HOVER).pack()

        # Atajos de teclado
        self.entry_user.bind("<Return>", lambda e: self.entry_pass.focus())
        self.entry_pass.bind("<Return>", lambda e: self.intentar_login())
        self.modal.bind("<Return>", lambda e: self.intentar_login())
        
        self.modal.after(50, self.entry_user.focus)

    def intentar_login(self):
        user = self.entry_user.get().strip()
        pwd = self.entry_pass.get().strip()

        if not user or not pwd:
            self.lbl_error.configure(text="Complete todos los campos.")
            return

        datos_usuario = verificar_credenciales(user, pwd)
        if datos_usuario:
            self.modal.destroy()
            self.callback_exito(datos_usuario)
        else:
            self.lbl_error.configure(text="Usuario o contraseña incorrectos.")