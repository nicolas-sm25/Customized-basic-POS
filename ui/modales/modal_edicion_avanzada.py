import customtkinter as ctk
from ui.componentes.creador_componentes import nuevo_frame, nuevo_label, nuevo_boton, nueva_caja_texto, COLOR_FALLO, COLOR_EXITO, COLOR_FALLO_HOVER
from ui.vistas.secciones.panel_autocompletado import PanelAutocompletado
from bll.gestor_productos import *

# --- SUB-MODAL DE CONFIRMACIÓN DE ELIMINACIÓN ---
class ModalConfirmacionEliminar(ctk.CTkToplevel):
    def __init__(self, master, callback_confirmar):
        super().__init__(master)
        self.title("¡Atención!")
        self.geometry("380x160")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()
        
        self.callback = callback_confirmar
        
        lbl = nuevo_label(self, "¿Estás absolutamente seguro de eliminar esto?\nEsta acción borrará el producto para siempre.", color_texto=COLOR_FALLO, fuente=("Arial", 13, "bold"))
        lbl.pack(pady=20)
        
        f_btns = nuevo_frame(self, color_fondo="transparent")
        f_btns.pack(fill="x", pady=10)
        
        btn_no = nuevo_boton(f_btns, "Cancelar", comando=self.destroy, color_fondo="#555555")
        btn_no.pack(side="left", expand=True, padx=15)
        
        btn_si = nuevo_boton(f_btns, "Sí, Eliminar", comando=self.confirmar, color_fondo=COLOR_FALLO, color_hover=COLOR_FALLO_HOVER)
        btn_si.pack(side="right", expand=True, padx=15)
        
    def confirmar(self):
        self.callback()
        self.destroy()

# --- MODAL PRINCIPAL ---
class ModalEdicionAvanzada(ctk.CTkToplevel):
    def __init__(self, master, producto_id, callback_actualizar):
        super().__init__(master)
        
        self.title("Edición Avanzada")
        self.geometry("500x650")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()
        
        self.producto_id = producto_id
        self.callback = callback_actualizar

        self.producto_datos = obtener_producto_por_id(producto_id)
        
        self.productos_unitarios = obtener_productos_unitarios()
        self.productos_unitarios = [p for p in self.productos_unitarios if p['id'] != self.producto_id]
        
        self.id_producto_base_seleccionado = None

        self.crear_interfaz()
        self.cargar_datos_actuales()
        self.validar_permiso_eliminacion()

    def crear_interfaz(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        frame_principal = nuevo_frame(self, color_fondo="transparent")
        frame_principal.grid(row=0, column=0, sticky="nsew", padx=20, pady=10)
        
        nuevo_label(frame_principal, "Edición Avanzada", fuente=("Arial", 20, "bold"), color_texto="#ffffff").pack(pady=(0, 10))
        
        # --- DATOS BÁSICOS ---
        frame_basico = nuevo_frame(frame_principal, color_fondo="#2b2b2b")
        frame_basico.pack(fill="x", pady=5, ipadx=10, ipady=10)
        
        nuevo_label(frame_basico, "Nombre del Producto:", poscicion="w").pack(fill="x", padx=10, pady=(5,0))
        self.entry_nombre = nueva_caja_texto(frame_basico)
        self.entry_nombre.pack(fill="x", padx=10, pady=(0, 10))
        
        nuevo_label(frame_basico, "Código de Barras (Opcional):", poscicion="w").pack(fill="x", padx=10, pady=(5,0))
        self.entry_codigo = nueva_caja_texto(frame_basico)
        self.entry_codigo.pack(fill="x", padx=10, pady=(0, 5))

        # --- DATOS RELACIONALES ---
        frame_relacional = nuevo_frame(frame_principal, color_fondo="#2b2b2b")
        frame_relacional.pack(fill="x", pady=10, ipadx=10, ipady=10)
        
        self.var_paquete = ctk.BooleanVar(value=False)
        self.switch_paquete = ctk.CTkSwitch(
            frame_relacional, 
            text="¿Es un paquete de otro producto?", 
            variable=self.var_paquete, 
            command=self.alternar_paquete, 
            font=("Arial", 12, "bold"), 
            progress_color=COLOR_EXITO
        )
        self.switch_paquete.pack(pady=10)

        self.frame_opciones_paquete = nuevo_frame(frame_relacional, color_fondo="transparent")
        
        self.lbl_titulo_base = nuevo_label(self.frame_opciones_paquete, "Busque y seleccione el producto base:", poscicion="w")
        self.lbl_titulo_base.pack(fill="x", padx=10, pady=(0, 5))

        self.entry_base_buscar = nueva_caja_texto(self.frame_opciones_paquete, placeholder="Ej: Coca Cola...")
        self.entry_base_buscar.pack(fill="x", padx=10, pady=(0, 5))

        self.entry_base_buscar.bind("<Return>", self.ejecutar_busqueda_base)
        self.entry_base_buscar.bind("<Escape>", self.resetear_buscador_base)

        self.lbl_titulo_cant = nuevo_label(self.frame_opciones_paquete, "Unidades por paquete:", poscicion="w")
        self.lbl_titulo_cant.pack(fill="x", padx=10, pady=(15, 5))
        
        self.entry_cant_paquete = nueva_caja_texto(self.frame_opciones_paquete, placeholder="Ej: 30")
        self.entry_cant_paquete.pack(fill="x", padx=10, pady=(0, 5))

        self.autocompletado_relacional = PanelAutocompletado(
            self.entry_base_buscar, 
            self.frame_opciones_paquete, 
            self.lbl_titulo_cant,
            self.resultado_autocompletado_base
        )

        # --- MENSAJE ---
        self.lbl_mensaje = nuevo_label(frame_principal, "", color_texto=COLOR_EXITO)
        self.lbl_mensaje.pack(pady=5)

        # --- BOTONES ---
        frame_botones = nuevo_frame(frame_principal, color_fondo="transparent")
        frame_botones.pack(fill="x", pady=10)
        
        self.btn_cancelar = nuevo_boton(frame_botones, "Cancelar", comando=self.destroy, color_fondo="#555555", color_hover="#333333")
        self.btn_cancelar.pack(side="left", expand=True, padx=5)

        self.btn_guardar = nuevo_boton(frame_botones, "Guardar", comando=self.guardar_cambios, color_fondo=COLOR_EXITO)
        self.btn_guardar.pack(side="left", expand=True, padx=5)

        self.btn_eliminar_inhabilitar = nuevo_boton(frame_botones, "Cargando...", comando=None, color_fondo=COLOR_FALLO, color_hover=COLOR_FALLO_HOVER)
        self.btn_eliminar_inhabilitar.pack(side="right", expand=True, padx=5)

    # --- LÓGICA AUTOCOMPLETADO ---
    def ejecutar_busqueda_base(self, event=None):
        """Dispara el Enter dentro del autocompletado relacional."""
        self.autocompletado_relacional.procesar_enter()

    def resetear_buscador_base(self, event=None):
        """Permite borrar la selección y buscar otro producto (Tecla ESC)."""
        self.id_producto_base_seleccionado = None
        self.entry_base_buscar.configure(state="normal", fg_color="#343638", text_color="#ffffff")
        self.entry_base_buscar.delete(0, 'end')
        self.entry_base_buscar.focus()

    def resultado_autocompletado_base(self, producto):
        """Callback: Se activa cuando seleccionan un producto base del menú flotante."""
        self.id_producto_base_seleccionado = producto['id']
        self.entry_base_buscar.delete(0, 'end')
        self.entry_base_buscar.insert(0, producto['nombre'])

        self.entry_cant_paquete.focus()

    # --- LÓGICA DE INTERFAZ Y BD ---
    def alternar_paquete(self):
        if self.var_paquete.get():
            self.frame_opciones_paquete.pack(fill="x", pady=5)
            self.resetear_buscador_base()

            if self.producto_datos and self.producto_datos.get('producto_base_id'):
                for p in self.productos_unitarios:
                    if p['id'] == self.producto_datos['producto_base_id']:
                        self.resultado_autocompletado_base(p)
                        break
        else:
            self.frame_opciones_paquete.pack_forget()

    def cargar_datos_actuales(self):
        if not self.producto_datos: return
        
        self.entry_nombre.insert(0, self.producto_datos['nombre'])
        if self.producto_datos['codigo_barras']:
            self.entry_codigo.insert(0, self.producto_datos['codigo_barras'])
            
        if self.producto_datos['es_paquete']:
            self.var_paquete.set(True)
            self.entry_cant_paquete.insert(0, str(self.producto_datos['cantidad_por_paquete']))
            self.alternar_paquete()

    def validar_permiso_eliminacion(self):
        tiene_ventas = verificar_ventas_producto(self.producto_id)
        es_activo = self.producto_datos.get('activo', True)
        
        if not tiene_ventas:
            self.btn_eliminar_inhabilitar.configure(
                text="Eliminar Definitivo", 
                command=self.solicitar_eliminacion, 
                fg_color=COLOR_FALLO,
                hover_color=COLOR_FALLO_HOVER
            )
        else:
            if es_activo:
                self.btn_eliminar_inhabilitar.configure(
                    text="Inhabilitar Producto", 
                    command=self.solicitar_cambio_estado, 
                    fg_color="#d4ac0d", 
                    hover_color="#b9770e"
                )
            else:
                self.btn_eliminar_inhabilitar.configure(
                    text="Reactivar Producto", 
                    command=self.solicitar_cambio_estado, 
                    fg_color=COLOR_EXITO, 
                    hover_color="#1e7e34"
                )


    def solicitar_cambio_estado(self):
        es_activacion = not self.producto_datos.get('activo', True)

        if es_activacion:
            exito, msg = reactivar_producto_db(self.producto_id)
        else:
            exito, msg = desactivar_producto_db(self.producto_id)
            
        if exito:
            self.callback(True, msg, False, None, None, es_cambio_estado=True)
            self.destroy()
        else:
            self.lbl_mensaje.configure(text=msg, text_color=COLOR_FALLO)

    def guardar_cambios(self):
        nombre = self.entry_nombre.get().strip()
        codigo = self.entry_codigo.get().strip()
        es_paquete = self.var_paquete.get()
        producto_base_id = None
        cant_paquete = 1
        
        if not nombre:
            self.lbl_mensaje.configure(text="El nombre es obligatorio.", text_color=COLOR_FALLO)
            return
            
        if es_paquete:
            nombre_digitado = self.entry_base_buscar.get().strip()
            base_valida = next((p for p in self.productos_unitarios if p['nombre'].lower() == nombre_digitado.lower()), None)
            
            if not base_valida:
                self.lbl_mensaje.configure(text="Producto base inválido. Seleccione uno de la lista.", text_color=COLOR_FALLO)
                return
            
            self.id_producto_base_seleccionado = base_valida['id']
            producto_base_id = self.id_producto_base_seleccionado
                    
            try:
                cant_paquete = int(self.entry_cant_paquete.get().strip())
                if cant_paquete <= 1: raise ValueError
            except ValueError:
                self.lbl_mensaje.configure(text="Cantidad de paquete inválida.", text_color=COLOR_FALLO)
                return

        exito, msg = actualizar_producto_avanzado(self.producto_id, nombre, codigo, es_paquete, producto_base_id, cant_paquete)
        if exito:
            self.callback(True, msg, False, nombre, codigo)
            self.destroy()
        else:
            self.lbl_mensaje.configure(text=msg, text_color=COLOR_FALLO)

    def solicitar_eliminacion(self):
        """Llama al sub-modal de confirmación antes de eliminar."""
        ModalConfirmacionEliminar(self, self.ejecutar_eliminacion)
        
    def ejecutar_eliminacion(self):
        """Se ejecuta solo si el usuario dijo 'Sí, Eliminar' en el sub-modal."""
        exito, msg = eliminar_producto_definitivo(self.producto_id)
        if exito:
            self.callback(True, msg, True, None, None)
            self.destroy()
        else:
            self.lbl_mensaje.configure(text=msg, text_color=COLOR_FALLO)