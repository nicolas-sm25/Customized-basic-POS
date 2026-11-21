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
from bll.gestor_impresora import (
    MODOS_IMPRESORA,
    listar_impresoras_windows,
    cargar_config_impresora,
    guardar_config_impresora,
    abrir_cajon_monedero,
    imprimir_ticket_prueba
)

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

        # --- SECCIÓN: IMPRESORA TÉRMICA Y CAJÓN MONEDERO ---
        nuevo_label(f_contenido, "Impresora Térmica y Cajón Monedero", fuente=("Arial", 16, "bold"), color_texto="#d4ac0d", poscicion="w").pack(anchor="w", pady=(25, 10))

        f_imp = nuevo_frame(f_contenido, color_fondo="#2b2b2b")
        f_imp.pack(fill="x", pady=5, padx=5)

        if rol_usuario == "Administrador":
            cfg_imp = cargar_config_impresora()

            f_imp_inner = nuevo_frame(f_imp, color_fondo="transparent")
            f_imp_inner.pack(fill="x", padx=15, pady=15)
            f_imp_inner.grid_columnconfigure(1, weight=1)

            # Fila 0: Selección de Impresora Windows + Botón refrescar
            nuevo_label(f_imp_inner, "Impresora instalada:", fuente=("Arial", 12, "bold"), poscicion="w").grid(row=0, column=0, sticky="w", pady=6, padx=(0, 10))

            f_sel_imp = nuevo_frame(f_imp_inner, color_fondo="transparent")
            f_sel_imp.grid(row=0, column=1, sticky="ew", pady=6)

            impresoras_win = listar_impresoras_windows()
            imp_actual = cfg_imp.get("nombre_impresora", "")
            if imp_actual and imp_actual not in impresoras_win:
                impresoras_win.insert(0, imp_actual)
            if not impresoras_win:
                impresoras_win = ["Sin impresora"]

            self.combo_impresora = ctk.CTkOptionMenu(
                f_sel_imp,
                values=impresoras_win,
                fg_color="#3b3b3b",
                button_color="#4b4b4b",
                button_hover_color="#5b5b5b",
                width=280
            )
            self.combo_impresora.set(imp_actual if imp_actual else impresoras_win[0])
            self.combo_impresora.pack(side="left", fill="x", expand=True)

            nuevo_boton(
                f_sel_imp,
                "Actualizar",
                comando=self.refrescar_lista_impresoras,
                color_fondo="#3498db",
                color_hover="#2980b9",
                ancho=40
            ).pack(side="left", padx=(8, 0))

            # Fila 1: Modo de Operación (4 opciones)
            nuevo_label(f_imp_inner, "Modo de operación:", fuente=("Arial", 12, "bold"), poscicion="w").grid(row=1, column=0, sticky="w", pady=6, padx=(0, 10))

            self.mapa_modos_ui = {etiqueta: clave for clave, etiqueta in MODOS_IMPRESORA.items()}
            modo_guardado = cfg_imp.get("modo", "desactivada")
            etiqueta_modo_actual = MODOS_IMPRESORA.get(modo_guardado, MODOS_IMPRESORA["desactivada"])

            self.combo_modo_imp = ctk.CTkOptionMenu(
                f_imp_inner,
                values=list(MODOS_IMPRESORA.values()),
                fg_color="#3b3b3b",
                button_color="#4b4b4b",
                button_hover_color="#5b5b5b"
            )
            self.combo_modo_imp.set(etiqueta_modo_actual)
            self.combo_modo_imp.grid(row=1, column=1, sticky="ew", pady=6)

            # Fila 2: Ancho de papel
            nuevo_label(f_imp_inner, "Ancho de papel:", fuente=("Arial", 12, "bold"), poscicion="w").grid(row=2, column=0, sticky="w", pady=6, padx=(0, 10))

            self.combo_ancho_papel = ctk.CTkOptionMenu(
                f_imp_inner,
                values=["80 mm (48 columnas - SAT Q23T)", "58 mm (32 columnas)"],
                fg_color="#3b3b3b",
                button_color="#4b4b4b",
                button_hover_color="#5b5b5b"
            )
            self.combo_ancho_papel.set("58 mm (32 columnas)" if int(cfg_imp.get("ancho_papel", 48)) == 32 else "80 mm (48 columnas - SAT Q23T)")
            self.combo_ancho_papel.grid(row=2, column=1, sticky="ew", pady=6)

            # Fila 3: NIT y Teléfono
            nuevo_label(f_imp_inner, "NIT / Régimen (Opcional):", fuente=("Arial", 12), poscicion="w").grid(row=3, column=0, sticky="w", pady=6, padx=(0, 10))
            self.entry_imp_nit = nueva_caja_texto(f_imp_inner, placeholder="Ej: 123.456.789-0 - No responsable de IVA")
            self.entry_imp_nit.insert(0, cfg_imp.get("nit", ""))
            self.entry_imp_nit.grid(row=3, column=1, sticky="ew", pady=6)

            # Fila 4: Dirección
            nuevo_label(f_imp_inner, "Dirección (Opcional):", fuente=("Arial", 12), poscicion="w").grid(row=4, column=0, sticky="w", pady=6, padx=(0, 10))
            self.entry_imp_dir = nueva_caja_texto(f_imp_inner, placeholder="Ej: Cra 10 # 20-30")
            self.entry_imp_dir.insert(0, cfg_imp.get("direccion", ""))
            self.entry_imp_dir.grid(row=4, column=1, sticky="ew", pady=6)

            # Fila 5: Teléfono
            nuevo_label(f_imp_inner, "Teléfono (Opcional):", fuente=("Arial", 12), poscicion="w").grid(row=5, column=0, sticky="w", pady=6, padx=(0, 10))
            self.entry_imp_tel = nueva_caja_texto(f_imp_inner, placeholder="Ej: 3001234567")
            self.entry_imp_tel.insert(0, cfg_imp.get("telefono", ""))
            self.entry_imp_tel.grid(row=5, column=1, sticky="ew", pady=6)

            # Fila 6: Mensaje pie de tirilla
            nuevo_label(f_imp_inner, "Mensaje pie de recibo:", fuente=("Arial", 12), poscicion="w").grid(row=6, column=0, sticky="w", pady=6, padx=(0, 10))
            self.entry_imp_pie = nueva_caja_texto(f_imp_inner, placeholder="Ej: ¡Gracias por su compra! Vuelva pronto")
            self.entry_imp_pie.insert(0, cfg_imp.get("mensaje_pie", ""))
            self.entry_imp_pie.grid(row=6, column=1, sticky="ew", pady=6)

            # Mensaje estado impresora
            self.lbl_mensaje_impresora = nuevo_label(f_imp, "", color_texto=COLOR_EXITO)
            self.lbl_mensaje_impresora.pack(pady=(2, 6))

            # Fila de Botones (Guardar / Probar Cajón / Imprimir Prueba)
            f_btns_imp = nuevo_frame(f_imp, color_fondo="transparent")
            f_btns_imp.pack(pady=(0, 15))

            nuevo_boton(
                f_btns_imp,
                "Guardar Configuración",
                comando=self.guardar_ajustes_impresora,
                color_fondo=COLOR_EXITO,
                color_hover=COLOR_EXITO_HOVER,
                ancho=180
            ).pack(side="left", padx=8)

            nuevo_boton(
                f_btns_imp,
                "Probar Cajón",
                comando=self.probar_cajon_ui,
                color_fondo="#d4ac0d",
                color_hover="#b9770e",
                ancho=140
            ).pack(side="left", padx=8)

            nuevo_boton(
                f_btns_imp,
                "Imprimir Prueba",
                comando=self.probar_impresion_ui,
                color_fondo="#3498db",
                color_hover="#2980b9",
                ancho=150
            ).pack(side="left", padx=8)
        else:
            nuevo_label(f_imp, "🔒 Acceso restringido.\nSolo los administradores pueden configurar la impresora.", fuente=("Arial", 13), color_texto=COLOR_FALLO).pack(pady=30)

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

    def refrescar_lista_impresoras(self):
        impresoras = listar_impresoras_windows()
        if not impresoras:
            impresoras = ["Sin impresora"]
        self.combo_impresora.configure(values=impresoras)
        self.combo_impresora.set(impresoras[0])
        self.lbl_mensaje_impresora.configure(text="Lista de impresoras actualizada.", text_color="#4fa6ff")

    def _recoger_datos_impresora_ui(self):
        imp_sel = self.combo_impresora.get()
        modo_clave = self.mapa_modos_ui.get(self.combo_modo_imp.get(), "desactivada")
        ancho = 32 if "58 mm" in self.combo_ancho_papel.get() else 48
        return {
            "nombre_impresora": "" if imp_sel == "Sin impresora" else imp_sel,
            "modo": modo_clave,
            "ancho_papel": ancho,
            "nit": self.entry_imp_nit.get().strip(),
            "direccion": self.entry_imp_dir.get().strip(),
            "telefono": self.entry_imp_tel.get().strip(),
            "mensaje_pie": self.entry_imp_pie.get().strip()
        }

    def guardar_ajustes_impresora(self):
        datos = self._recoger_datos_impresora_ui()
        exito, msg = guardar_config_impresora(datos)
        self.lbl_mensaje_impresora.configure(text=msg, text_color=COLOR_EXITO if exito else COLOR_FALLO)

        ventana = self.winfo_toplevel()
        if hasattr(ventana, "actualizar_estado_boton_cajon"):
            ventana.actualizar_estado_boton_cajon()

    def probar_cajon_ui(self):
        datos = self._recoger_datos_impresora_ui()
        exito, msg = abrir_cajon_monedero(forzar_manual=True, nombre_impresora_override=datos["nombre_impresora"])
        self.lbl_mensaje_impresora.configure(
            text="Pulso enviado al cajón monedero." if exito else msg,
            text_color=COLOR_EXITO if exito else COLOR_FALLO
        )

    def probar_impresion_ui(self):
        datos = self._recoger_datos_impresora_ui()
        exito, msg = imprimir_ticket_prueba(config_override=datos)
        self.lbl_mensaje_impresora.configure(
            text="Ticket de prueba enviado a la impresora." if exito else msg,
            text_color=COLOR_EXITO if exito else COLOR_FALLO
        )