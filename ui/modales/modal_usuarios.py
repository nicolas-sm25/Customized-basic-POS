import customtkinter as ctk
from ui.componentes.creador_componentes import *
from bll.gestor_usuarios import obtener_usuarios, cambiar_estado_usuario

class ModalUsuarios:
    def __init__(self, master):
        self.modal = nuevo_modal(master, "Gestión de Usuarios", 650, 400)
        
        lbl_titulo = nuevo_label(self.modal, "Usuarios Registrados en el Sistema", fuente=FUENTE_TITULOS)
        lbl_titulo.pack(pady=15)
        
        self.lbl_mensaje = nuevo_label(self.modal, "")
        self.lbl_mensaje.pack(pady=2)

        self.scroll_tabla = ctk.CTkScrollableFrame(self.modal, fg_color="#202020", corner_radius=10)
        self.scroll_tabla.pack(fill="both", expand=True, padx=20, pady=10)
        
        nuevo_boton(self.modal, "Cerrar", comando=self.modal.destroy, color_fondo="#555555", color_hover="#777777").pack(pady=10)
        self.cargar_tabla()
        
    def cargar_tabla(self):
        for w in self.scroll_tabla.winfo_children():
            w.destroy()
            
        try:
            usuarios = obtener_usuarios()
        except Exception as e:
            self.lbl_mensaje.configure(text=f"Error cargando usuarios: {e}", text_color=COLOR_FALLO)
            return
            
        f_enc = nuevo_frame(self.scroll_tabla, color_fondo="#1a1a1a")
        f_enc.pack(fill="x", pady=(0, 5))
        
        cols = [3, 2, 2, 2] # Proporciones de las columnas
        for i, w in enumerate(cols): 
            f_enc.grid_columnconfigure(i, weight=w, uniform="usu")
        
        # CABECERAS
        nuevo_label(f_enc, "Nombre Completo", fuente=("Arial", 12, "bold"), color_texto="#a0a0a0", poscicion="w").grid(row=0, column=0, sticky="w", padx=10, pady=8)
        nuevo_label(f_enc, "Usuario", fuente=("Arial", 12, "bold"), color_texto="#a0a0a0", poscicion="center").grid(row=0, column=1, sticky="nsew", pady=8)
        nuevo_label(f_enc, "Rol", fuente=("Arial", 12, "bold"), color_texto="#a0a0a0", poscicion="center").grid(row=0, column=2, sticky="nsew", pady=8)
        nuevo_label(f_enc, "Acción", fuente=("Arial", 12, "bold"), color_texto="#a0a0a0", poscicion="center").grid(row=0, column=3, sticky="nsew", pady=8)
            
        for u in usuarios:
            activo = u.get('activo', True)
            nombre = u.get('nombre', 'Desconocido')
            username = u.get('username', '')
            rol = u.get('rol', 'Vendedor')
            uid = u.get('id')

            color_fila = "#2b2b2b" if activo else "#1c1c1c"
            f_item = nuevo_frame(self.scroll_tabla, color_fondo=color_fila)
            f_item.pack(fill="x", pady=3)
            
            for i, w in enumerate(cols): 
                f_item.grid_columnconfigure(i, weight=w, uniform="usu")
            
            col_txt = "#ffffff" if activo else "#666666"
            nombre_mostrar = f"{nombre}{' (Inactivo)' if not activo else ''}"
            
            nuevo_label(f_item, nombre_mostrar, color_texto=col_txt, poscicion="w").grid(row=0, column=0, sticky="w", padx=10, pady=10)
            nuevo_label(f_item, username, color_texto=col_txt, poscicion="center").grid(row=0, column=1, sticky="nsew")
            nuevo_label(f_item, rol, color_texto="#d4ac0d" if rol == "Administrador" else col_txt, poscicion="center").grid(row=0, column=2, sticky="nsew")

            f_btn = nuevo_frame(f_item, color_fondo="transparent")
            f_btn.grid(row=0, column=3, sticky="nsew", pady=5)
            
            txt_btn = "X" if activo else "✓"
            col_btn = COLOR_FALLO if activo else COLOR_EXITO
            hov_btn = COLOR_FALLO_HOVER if activo else COLOR_EXITO_HOVER
            
            nuevo_boton(f_btn, txt_btn, comando=lambda user_id=uid, act=activo: self.alternar_estado(user_id, act), color_fondo=col_btn, color_hover=hov_btn, ancho=40).pack(expand=True)

    def alternar_estado(self, uid, estado_actual):
        exito, msj = cambiar_estado_usuario(uid, not estado_actual)
        self.lbl_mensaje.configure(text=msj, text_color=COLOR_EXITO if exito else COLOR_FALLO)
        if exito: 
            self.cargar_tabla()