from bll.gestor_productos import buscar_producto_por_codigo, buscar_productos_por_nombre
from bll.gestor_caja import obtener_caja_abierta, abrir_caja, cerrar_caja
from ui.configuracion_componentes import *
from ui.creador_componentes import *


# --- CREACION VISTA CAJA ---
class VistaCaja(ConfiguracionComponentes):
    def __init__(self, master):
        super().__init__(master)
        
        self.frame_principal = nuevo_frame(self)
        self.frame_principal.pack(fill="both", expand=True)

        self.verificar_estado_caja()
        
        self.entradas_editables = [
                    self.entry_buscar_prod
                ]
        
    # --- VERIFICAR SI LA CAJA ESTÁ ACTIVA ---
    def verificar_estado_caja(self):
        """Consulta al BLL y dibuja la interfaz correspondiente."""
        caja_activa = obtener_caja_abierta()
        
        for widget in self.frame_principal.winfo_children():
            widget.destroy()
            
        if caja_activa:
            self.mostrar_pantalla_ventas(caja_activa)
        else:
            self.mostrar_pantalla_apertura()

    # --- MENÚ APERTURA DE CAJA ---
    def mostrar_pantalla_apertura(self):
        frame_centro = nuevo_frame(self.frame_principal)
        frame_centro.pack(expand=True)

        self.lbl_titulo = nuevo_label(frame_centro, "Abrir caja", fuente=FUENTE_TITULOS)
        self.lbl_titulo.pack(pady=20)

        self.lbl_instruccion = nuevo_label(frame_centro, "Ingrese el valor efectivo inicial que se encuentra en la caja:")
        self.lbl_instruccion.pack(pady=10)

        self.entry_base = nueva_caja_texto(frame_centro, placeholder="Ej: 50000")
        self.entry_base.pack(pady=10)
        self.entry_base.bind("<Return>", self.ejecutar_apertura)

        self.btn_abrir = nuevo_boton(
            frame_centro, 
            "Abrir caja", 
            comando=self.ejecutar_apertura, 
            color_fondo=COLOR_EXITO, 
            color_hover=COLOR_EXITO_HOVER
        )
        self.btn_abrir.pack(pady=20)

        self.lbl_mensaje = nuevo_label(frame_centro, "")
        self.lbl_mensaje.pack(pady=5)
        
        self.after(1, self.entry_base.focus)

    def ejecutar_apertura(self, event=None):
        base_str = self.entry_base.get().strip()
        if not base_str:
            self.lbl_mensaje.configure(text="Ingrese el efectivo actual en caja (Si no hay efectivo, ingrese 0)", text_color=COLOR_FALLO)
            return

        try:
            base_efectivo = float(base_str)
            if base_efectivo < 0:
                self.lbl_mensaje.configure(text="La base no puede ser negativa.", text_color=COLOR_FALLO)
                return
            
            exito, mensaje = abrir_caja(base_efectivo)
            
            if exito:
                self.verificar_estado_caja()
            else:
                self.lbl_mensaje.configure(text=mensaje, text_color=COLOR_FALLO)

        except ValueError:
            self.lbl_mensaje.configure(text="Ingrese un monto numérico válido.", text_color=COLOR_FALLO)

    # --- MENÚ VENTAS ---
    def mostrar_pantalla_ventas(self, caja_activa):
        self.carrito = [] # * ---> Inicializacion del carrito

        self.frame_principal.grid_columnconfigure(0, weight=3, uniform="grupo1")
        self.frame_principal.grid_columnconfigure(1, weight=1, uniform="grupo1")
        self.frame_principal.grid_rowconfigure(0, weight=1)

        # --- FRAMES ---
        frame_izquierdo = nuevo_frame(self.frame_principal)
        frame_izquierdo.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        frame_derecho = nuevo_frame(self.frame_principal)
        frame_derecho.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        frame_busqueda = nuevo_frame(frame_izquierdo)
        frame_busqueda.pack(fill="x", pady=(0, 10))
        
        self.frame_carrito = nuevo_frame(frame_izquierdo, color_fondo="#202020")
        self.frame_carrito.pack(fill="both", expand=True)
        
        frame_totales = nuevo_frame(frame_derecho, color_fondo="transparent")
        frame_totales.pack(side="top", fill="both", expand=True)
        
        # --- BUSQUEDA Y AGREGAR AL CARRITO ---
        self.entry_buscar_prod = nueva_caja_texto(frame_busqueda, placeholder="Código de Barras o Nombre...")
        self.entry_buscar_prod.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.entry_buscar_prod.bind("<Return>", self.agregar_al_carrito)
        
        self.btn_agregar = nuevo_boton(frame_busqueda, "Agregar", self.agregar_al_carrito)
        self.btn_agregar.pack(side="right")

        # --- INFO DEL CARRITO (TEMPORAL) ---
        lbl_carrito = nuevo_label(self.frame_carrito, "El carrito está vacío", fuente=FUENTE_NEGRITA)
        lbl_carrito.pack(expand=True)

        # --- TEXTO Y BOTONES PANEL DERECHO ---
        self.lbl_texto_total = nuevo_label(frame_totales, "Total:", fuente=FUENTE_TITULOS)
        self.lbl_texto_total.pack(pady=(40, 0))
        
        self.lbl_valor_total = nuevo_label(frame_totales, "$0", fuente=("Arial", 30, "bold"), color_texto=COLOR_EXITO)
        self.lbl_valor_total.pack(pady=(0, 40))
        
        self.btn_abrir_cobro = nuevo_boton(
            frame_totales, 
            "Cobrar Venta", 
            comando=self.abrir_modal_cobro,
            color_fondo=COLOR_EXITO,
            color_hover=COLOR_EXITO_HOVER
        )
        self.btn_abrir_cobro.pack(pady=10)
        
        self.btn_cerrar_caja = nuevo_boton(
            frame_derecho, 
            "Cerrar caja", 
            comando=self.confirmar_cierre_caja,
            color_fondo=COLOR_FALLO,
            color_hover=COLOR_FALLO_HOVER
        )
        self.btn_cerrar_caja.pack(side="bottom", pady=20, padx=20, anchor="se")

    # --- POP-UP COBRO ---
    def abrir_modal_cobro(self):

        # Evitar cobro con el carrito vacio
        if not hasattr(self, 'carrito') or not self.carrito:
            self.lbl_valor_total.configure(text="¡Vacío!", text_color=COLOR_FALLO)
            self.after(1500, lambda: self.lbl_valor_total.configure(text="$0", text_color=COLOR_EXITO))
            return
        
        modal = ctk.CTkToplevel(self)
        modal.title("Cobrar Venta")
        modal.geometry("400x300")
        modal.transient(self.winfo_toplevel())
        modal.grab_set()

        # Atajos de teclado
        modal.bind("<Escape>", lambda event: modal.destroy())
        # modal.bind("<Return>", lambda event: print("Lógica cobrar efectivo (Atajo Enter)")) ---> Se implementa luego

        # Diseño del pop-up
        frame_modal = nuevo_frame(modal)
        frame_modal.pack(expand=True, fill="both", padx=20, pady=20)

        lbl_titulo = nuevo_label(frame_modal, "Seleccione Método de Pago", fuente=FUENTE_TITULOS)
        lbl_titulo.pack(pady=10)

        total_actual = self.lbl_valor_total.cget("text")
        lbl_monto = nuevo_label(frame_modal, f"Monto a cobrar: {total_actual}", fuente=("Arial", 24, "bold"), color_texto=COLOR_EXITO)
        lbl_monto.pack(pady=20)

        frame_botones = nuevo_frame(frame_modal, color_fondo="transparent")
        frame_botones.pack(pady=10)

        # Pago por efectivo
        btn_efectivo = nuevo_boton(
            frame_botones, 
            "Efectivo (Enter)", 
            comando=lambda: print("Lógica cobrar efectivo"),
            color_fondo=COLOR_EXITO,
            color_hover=COLOR_EXITO_HOVER
        )
        btn_efectivo.grid(row=0, column=0, padx=10)

        # Pago por Nequi
        btn_nequi = nuevo_boton(
            frame_botones, 
            "Nequi", 
            comando=lambda: print("Lógica cobrar nequi"),
            color_fondo="#5e17eb", 
            color_hover="#4a11c0"
        )
        btn_nequi.grid(row=0, column=1, padx=10)

        # Regresar al carrito
        btn_regresar = nuevo_boton(
            frame_modal, 
            "Regresar (Esc)", 
            comando=modal.destroy,
            color_fondo=COLOR_FALLO,
            color_hover=COLOR_FALLO_HOVER
        )
        btn_regresar.pack(side="bottom", pady=10)
    
    # --- POP-UP CIERRE DE CAJA ---    
    def confirmar_cierre_caja(self):
        
        modal = ctk.CTkToplevel(self)
        modal.title("Confirmar Acción")
        modal.geometry("450x250")
        modal.transient(self.winfo_toplevel()) 
        modal.grab_set()

        # Atajos de teclado
        modal.bind("<Escape>", lambda event: modal.destroy())
        modal.bind("<Return>", lambda event: modal.destroy()) 

        # Diseño del pop-up
        frame_modal = nuevo_frame(modal)
        frame_modal.pack(expand=True, fill="both", padx=20, pady=20)
        
        lbl_pregunta = nuevo_label(
            frame_modal, 
            "¿Seguro que quieres cerrar la caja?", 
            fuente=FUENTE_TITULOS
        )
        lbl_pregunta.pack(pady=30)
        
        frame_botones = nuevo_frame(frame_modal)
        frame_botones.pack(pady=10)

        # Cancelar cierre de caja
        btn_regresar = nuevo_boton(
            frame_botones, 
            "Regresar", 
            comando=modal.destroy, 
            color_fondo=COLOR_EXITO,
            color_hover=COLOR_EXITO_HOVER
        )
        btn_regresar.grid(row=0, column=0, padx=20)

        # Confirmar cierre de caja
        def confirmar_y_cerrar():
            modal.destroy()
            self.ejecutar_cierre()

        btn_cerrar = nuevo_boton(
            frame_botones, 
            "Sí, Cerrar Caja", 
            comando=confirmar_y_cerrar,
            color_fondo=COLOR_FALLO,
            color_hover=COLOR_FALLO_HOVER
        )
        btn_cerrar.grid(row=0, column=1, padx=20)
    
    # Ejecutar cierre de caja
    def ejecutar_cierre(self):
        """Llama al BLL para cerrar la caja y devuelve al usuario a la pantalla de inicio."""
        exito, mensaje = cerrar_caja()
        
        if exito:
            self.verificar_estado_caja()
        else:
            print(f"Error al cerrar: {mensaje}")

    # --- CARRITO DE COMPRAS ---
    def agregar_al_carrito(self, event=None):
        """Busca el producto y lo mete al carrito (o suma +1 si ya existe)."""
        criterio = self.entry_buscar_prod.get().strip()
        if not criterio:
            return

        # Busqueda en la DB
        producto = buscar_producto_por_codigo(criterio)
        if not producto:
            resultados = buscar_productos_por_nombre(criterio)
            if resultados:
                producto = resultados[0]

        # Busqueda en el carrito
        if producto:
            for item in self.carrito:
                if item["id"] == producto["id"]:
                    item["cantidad"] += 1
                    item["subtotal"] = item["cantidad"] * item["precio_venta"]
                    break
            else:
                # Agrega nuevo elemento
                self.carrito.append({
                    "id": producto["id"],
                    "nombre": producto["nombre"],
                    "precio_venta": producto["precio_venta"],
                    "costo": producto["costo"],
                    "cantidad": 1,
                    "subtotal": producto["precio_venta"]
                })
            
            # Actualiza UI
            self.entry_buscar_prod.delete(0, 'end')
            self.actualizar_ui_carrito()
        else:
            # Mensaje de error
            self.entry_buscar_prod.delete(0, 'end')
            self.entry_buscar_prod.configure(placeholder_text="¡Producto no encontrado!", placeholder_text_color = COLOR_FALLO)
            self.after(1000, lambda: [self.focus(), self.entry_buscar_prod.configure(placeholder_text="Código de Barras o Nombre...", placeholder_text_color = "gray"), self.entry_buscar_prod.focus()])

    # --- ACTUALIZACION DE UI ---
    def actualizar_ui_carrito(self):
        """Redibuja la lista de productos y recalcula el gran total."""
        
        # Limpieza inicial
        for widget in self.frame_carrito.winfo_children():
            widget.destroy()

        if not self.carrito:
            lbl_vacio = nuevo_label(self.frame_carrito, "El carrito está vacío", fuente=FUENTE_NEGRITA)
            lbl_vacio.pack(expand=True)
            self.lbl_valor_total.configure(text="$0")
            return

        # Añadir producto visualmente
        total_venta = 0.0
        
        for index, item in enumerate(self.carrito):
            frame_item = nuevo_frame(self.frame_carrito, color_fondo="#3b3b3b")
            frame_item.pack(fill="x", padx=5, pady=2)
            
            texto_item = f"{item['nombre']} | P.U: ${int(item['precio_venta'])} | Sub: ${int(item['subtotal'])}"
            lbl_item = nuevo_label(frame_item, texto_item, poscicion="w")
            lbl_item.pack(side="left", padx=10, pady=5)
            
            # --- CONTROLES DE CANTIDAD ---
            frame_controles = nuevo_frame(frame_item, color_fondo="transparent")
            frame_controles.pack(side="right", padx=5, pady=5)

            # Botón eliminar del carrito
            btn_eliminar = nuevo_boton(
                frame_controles, 
                "X", 
                comando=lambda i=index: self.eliminar_del_carrito(i),
                color_fondo=COLOR_FALLO,
                color_hover=COLOR_FALLO_HOVER,
                ancho=30
            )
            btn_eliminar.pack(side="right", padx=(10, 0))

            # Botón [+]
            btn_mas = nuevo_boton(
                frame_controles, 
                "+", 
                comando=lambda i=index: self.cambiar_cantidad(i, 1),
                ancho=30
            )
            btn_mas.pack(side="right", padx=2)

            # Caja de texto para cantidad manual
            entry_cant = nueva_caja_texto(frame_controles)
            entry_cant.configure(width=50)
            entry_cant.insert(0, str(item['cantidad']))
            entry_cant.pack(side="right", padx=2)
            entry_cant.bind("<Return>", lambda event, i=index, e=entry_cant: self.actualizar_cantidad_manual(e, i))

            # Botón [-]
            btn_menos = nuevo_boton(
                frame_controles, 
                "-", 
                comando=lambda i=index: self.cambiar_cantidad(i, -1),
                ancho=30
            )
            btn_menos.pack(side="right", padx=2)

            total_venta += item["subtotal"]

        # Actualizacion del total
        self.lbl_valor_total.configure(text=f"${int(total_venta):,}".replace(",", "."))

    # --- QUITAR PRODUCTO ---
    def eliminar_del_carrito(self, index):
        """Elimina un producto del carrito por su posición y refresca la UI."""
        self.carrito.pop(index)
        self.actualizar_ui_carrito()

    # --- CAMBIAR CANTIDAD DE PRODUCTO ---
    def cambiar_cantidad(self, index, cambio):
        """Suma o resta 1 a la cantidad mediante los botones."""
        nueva_cantidad = self.carrito[index]["cantidad"] + cambio
        
        if nueva_cantidad > 0:
            self.carrito[index]["cantidad"] = nueva_cantidad
            self.carrito[index]["subtotal"] = nueva_cantidad * self.carrito[index]["precio_venta"]
            self.actualizar_ui_carrito()

    def actualizar_cantidad_manual(self, entry, index):
        """Actualiza la cantidad leyendo el valor escrito en el Entry tras presionar Enter."""
        valor_str = entry.get().strip()
        
        try:
            nueva_cantidad = int(valor_str)
            if nueva_cantidad > 0:
                self.carrito[index]["cantidad"] = nueva_cantidad
                self.carrito[index]["subtotal"] = nueva_cantidad * self.carrito[index]["precio_venta"]
        except ValueError:
            pass
            
        self.actualizar_ui_carrito()
        self.entry_buscar_prod.focus()