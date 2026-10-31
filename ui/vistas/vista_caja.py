# Gestores (lógica)
from bll.gestor_ventas import registrar_venta, obtener_ventas_pendientes, eliminar_venta_pendiente
from bll.gestor_productos import buscar_producto_por_codigo, buscar_productos_por_nombre
from bll.gestor_caja import *
# Componentes
from ui.componentes.configuracion_componentes import *
from ui.componentes.creador_componentes import *
# Modales/Pop-ups
from ui.modales.modal_cobro import ModalCobro
from ui.modales.modal_cierre import ModalCierre
from ui.modales.modal_guardar import ModalGuardar
from ui.modales.modal_ventas_guardadas import ModalVentasGuardadas
# Gestores (vista)
from ui.vistas.secciones.gestor_carrito import GestorCarrito
from ui.vistas.secciones.gestor_recibo import GestorRecibo

# --- CREACION VISTA CAJA ---
class VistaCaja(ConfiguracionComponentes):
    def __init__(self, master):
        super().__init__(master)
        
        self.frame_principal = nuevo_frame(self)
        self.frame_principal.pack(fill="both", expand=True)

        self.verificar_estado_caja()

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
        self.entry_base.bind("<KeyRelease>", lambda event: self.formatear_entrada_moneda(self.entry_base))

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
        base_str = self.entry_base.get().replace(".", "").strip()
        if not base_str:
            self.lbl_mensaje.configure(text="Ingrese el efectivo actual en caja", text_color=COLOR_FALLO)
            return

        try:
            base_efectivo = float(base_str)
            if base_efectivo < 0:
                self.lbl_mensaje.configure(text="La base no puede ser negativa.", text_color=COLOR_FALLO)
                return

            ventana_ppal = self.winfo_toplevel()
            usuario_id = getattr(ventana_ppal, 'usuario_actual', {}).get('id')
            
            exito, mensaje = abrir_caja(base_efectivo, usuario_id=usuario_id)
            
            if exito:
                self.verificar_estado_caja()
            else:
                self.lbl_mensaje.configure(text=mensaje, text_color=COLOR_FALLO)

        except ValueError:
            self.lbl_mensaje.configure(text="Ingrese un monto numérico válido.", text_color=COLOR_FALLO)

    # --- MENÚ VENTAS ---
    def mostrar_pantalla_ventas(self, caja_activa):
        self.carrito = [] # * ---> Inicializacion del carrito

        self.caja_activa_id = caja_activa.id

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
        self.after(5, self.entry_buscar_prod.focus)
        
        self.btn_agregar = nuevo_boton(frame_busqueda, "Agregar", self.agregar_al_carrito)
        self.btn_agregar.pack(side="right")

        # --- TEXTO Y BOTONES PANEL DERECHO ---
        self.lbl_texto_total = nuevo_label(frame_totales, "Total:", fuente=FUENTE_TITULOS)
        self.lbl_texto_total.pack(pady=(15, 0))
        
        self.lbl_valor_total = nuevo_label(frame_totales, "$0", fuente=("Arial", 30, "bold"), color_texto=COLOR_EXITO)
        self.lbl_valor_total.pack(pady=(0, 15))

        self.btn_abrir_cobro = nuevo_boton(
            frame_totales, 
            "Cobrar Venta (F12)", 
            comando=self.abrir_modal_cobro,
            color_fondo=COLOR_EXITO,
            color_hover=COLOR_EXITO_HOVER
        )
        self.btn_abrir_cobro.pack(fill="x", padx=20, pady=5, ipady=5)
        self.winfo_toplevel().bind("<F12>", lambda event: self.abrir_modal_cobro())

        self.btn_guardar = nuevo_boton(
            frame_totales, 
            "Guardar Venta (F11)", 
            comando=self.abrir_modal_espera,
            color_fondo="#d4ac0d", 
            color_hover="#b9770e"
        )
        self.btn_guardar.pack(fill="x", padx=20, pady=5, ipady=5)
        self.winfo_toplevel().bind("<F11>", lambda event: self.abrir_modal_espera())
        
        self.btn_ver_guardadas = nuevo_boton(
            frame_totales, 
            "Ver Ventas Guardadas", 
            comando=self.abrir_modal_ver_guardadas,
            color_fondo="#db4e17", 
            color_hover="#922F10"
        )
        self.btn_ver_guardadas.pack(fill="x", padx=20, pady=5, ipady=5)

        self.btn_gastos = nuevo_boton(
            frame_totales, 
            "Registrar Gasto Rápido", 
            comando=self.abrir_modal_gastos,
            color_fondo="#5e17eb", 
            color_hover="#4a11c0"
        )
        self.btn_gastos.pack(fill="x", padx=20, pady=5, ipady=5)

        self.btn_cerrar_caja = nuevo_boton(
            frame_derecho, 
            "Cerrar Caja", 
            comando=self.confirmar_cierre_caja,
            color_fondo=COLOR_FALLO,
            color_hover=COLOR_FALLO_HOVER
        )
        self.btn_cerrar_caja.pack(fill="x", padx=20, pady=5, ipady=5)
        
        # --- INICIALIZACION CARRITO ---
        self.gestor_carrito = GestorCarrito(self.frame_carrito, self.lbl_valor_total, self.entry_buscar_prod)
        self.gestor_carrito.btn_ver_guardadas = self.btn_ver_guardadas
        self.gestor_carrito.actualizar_ui()
        
        # --- INICIALIZACION GESTOR DEL MINI RECIBO ---
        self.gestor_recibo = GestorRecibo(frame_totales)

    # --- POP-UP COBRO ---
    def abrir_modal_cobro(self):

        # Evitar cobro con el carrito vacio
        if not hasattr(self, 'gestor_carrito') or not self.gestor_carrito.items:
            self.lbl_valor_total.configure(text="¡Vacío!", text_color=COLOR_FALLO)
            self.after(1500, lambda: self.lbl_valor_total.configure(text="$0", text_color=COLOR_EXITO))
            return
        
        total_actual = self.lbl_valor_total.cget("text")
        ModalCobro(self, total_actual, self.procesar_cobro)

    # --- POP-UP GUARDAR ---
    def abrir_modal_espera(self):
        """Abre el modal personalizado para guardar ventas fiadas."""
        if not hasattr(self, 'gestor_carrito') or not self.gestor_carrito.items:
            self.lbl_valor_total.configure(text="¡Vacío!", text_color=COLOR_FALLO)
            self.after(1500, lambda: self.lbl_valor_total.configure(text="$0", text_color=COLOR_EXITO))
            return
        
        ModalGuardar(self, self.procesar_espera)

    def procesar_espera(self, referencia, modal_referencia):
        """Envía los datos al BLL y muestra el éxito en la UI."""
        exito, mensaje = registrar_venta(
            carrito=self.gestor_carrito.items,
            metodo_pago="Pendiente",
            caja_id=self.caja_activa_id,
            nombre_cliente=referencia,
            pagado=False
        )

        if exito:
            self.gestor_carrito.vaciar()
            modal_referencia.cerrar_modal()
            
            # --- MENSAJE DE ÉXITO ---
            self.entry_buscar_prod.delete(0, 'end')
            self.entry_buscar_prod.configure(placeholder_text=f"¡Guardado!, referencia: {referencia}", placeholder_text_color=COLOR_EXITO)

            self.after(2000, lambda: [
                self.focus(), 
                self.entry_buscar_prod.configure(placeholder_text="Código de Barras o Nombre...", placeholder_text_color="gray"), 
                self.entry_buscar_prod.focus()
            ])
        else:
            modal_referencia.lbl_error.configure(text=mensaje)

    # --- POP-UP GASTOS ---
    def abrir_modal_gastos(self):
        from ui.modales.modal_gasto import ModalGasto
        ModalGasto(self, self.caja_activa_id, self.confirmar_gasto)
        
    def confirmar_gasto(self, exito, mensaje):
        if exito:
            self.entry_buscar_prod.configure(placeholder_text="¡Gasto registrado en caja!", placeholder_text_color=COLOR_EXITO)
        else:
            self.entry_buscar_prod.configure(placeholder_text="Error al registrar gasto", placeholder_text_color=COLOR_FALLO)
        self.after(2000, lambda: self.entry_buscar_prod.configure(placeholder_text="Código de Barras o Nombre...", placeholder_text_color="gray"))

    # --- POP-UP PEDIDOS GUARDADOS ---
    def abrir_modal_ver_guardadas(self):
        from ui.modales.modal_ventas_guardadas import ModalVentasGuardadas
        ventas_pendientes = obtener_ventas_pendientes()
        ModalVentasGuardadas(self, ventas_pendientes, self.recuperar_venta, self.eliminar_venta_guardada)

    def recuperar_venta(self, venta):
        self.gestor_carrito.cargar_items(venta["items"])
        self.cliente_actual = venta["cliente"]
        eliminar_venta_pendiente(venta["id"])
        
        self.entry_buscar_prod.delete(0, 'end')
        self.entry_buscar_prod.configure(placeholder_text=f"¡Pedido de {venta['cliente']} recuperado!", placeholder_text_color=COLOR_EXITO)
        
        self.after(1500, lambda: [
            self.focus(), 
            self.entry_buscar_prod.configure(placeholder_text="Código de Barras o Nombre...", placeholder_text_color="gray"), 
            self.entry_buscar_prod.focus()
        ])

    def eliminar_venta_guardada(self, venta_id):
        exito = eliminar_venta_pendiente(venta_id)
        if exito:
            self.entry_buscar_prod.configure(placeholder_text="¡Pedido eliminado!", placeholder_text_color=COLOR_EXITO)
        else:
            self.entry_buscar_prod.configure(placeholder_text="Error al eliminar", placeholder_text_color=COLOR_FALLO)
        
        self.after(1500, lambda: [
            self.focus(), 
            self.entry_buscar_prod.configure(placeholder_text="Código de Barras o Nombre...", placeholder_text_color="gray"), 
            self.entry_buscar_prod.focus()
        ])

    # --- POP-UP CIERRE CAJA ---
    def confirmar_cierre_caja(self):
        from ui.modales.modal_cierre import ModalCierre
        ModalCierre(self, self.caja_activa_id, self.ejecutar_cierre)
    
    def ejecutar_cierre(self, efectivo_fisico, diferencia):
        from bll.gestor_caja import cerrar_caja_definitiva
        exito, mensaje = cerrar_caja_definitiva(self.caja_activa_id, efectivo_fisico, diferencia)
        
        if exito:
            self.verificar_estado_caja()
        else:
            print(f"Error al cerrar: {mensaje}")

    # --- CARRITO DE COMPRAS ---
    def agregar_al_carrito(self, event=None):
        """Busca el producto y delega la interfaz al GestorCarrito."""
        criterio = self.entry_buscar_prod.get().strip()
        if not criterio:
            return

        producto = buscar_producto_por_codigo(criterio)
        if not producto:
            resultados = buscar_productos_por_nombre(criterio)
            if resultados:
                producto = resultados[0]

        if producto:
            self.gestor_carrito.agregar_producto(producto)
            self.entry_buscar_prod.delete(0, 'end')
        else:
            self.entry_buscar_prod.delete(0, 'end')
            self.focus()
            self.entry_buscar_prod.configure(placeholder_text="¡Producto no encontrado!", placeholder_text_color=COLOR_FALLO)
            self.after(1000, lambda: [
                self.master.focus(), 
                self.entry_buscar_prod.configure(placeholder_text="Código de Barras o Nombre...", placeholder_text_color="gray"), 
                self.entry_buscar_prod.focus()
            ])

    def procesar_cobro(self, metodo_pago, modal_referencia, entregado=0, vueltas=0):
        """Envía los items guardados en el gestor al BLL y muestra las vueltas."""
        items_carrito = self.gestor_carrito.items
        
        if not items_carrito:
            return

        total_venta = sum(item['subtotal'] for item in items_carrito)

        exito, mensaje = registrar_venta(
            carrito=items_carrito, 
            metodo_pago=metodo_pago, 
            caja_id=self.caja_activa_id
        )

        if exito:
            cliente_venta = getattr(self, 'cliente_actual', None)

            # Enviar datos al mini recibo
            self.gestor_recibo.actualizar_recibo(
                items=items_carrito,
                total=total_venta,
                metodo_pago=metodo_pago,
                entregado=entregado,
                vueltas=vueltas,
                cliente=cliente_venta
            )

            self.gestor_carrito.vaciar()
            modal_referencia.cerrar_modal()
            
            if hasattr(self, 'cliente_actual'):
                del self.cliente_actual

            self.entry_buscar_prod.delete(0, 'end')
            self.entry_buscar_prod.configure(placeholder_text="¡Venta Exitosa!", placeholder_text_color=COLOR_EXITO)

            self.after(2000, lambda: [
                self.master.focus(),
                self.entry_buscar_prod.configure(placeholder_text="Código de Barras o Nombre...", placeholder_text_color="gray"),
                self.entry_buscar_prod.focus()
            ])
        else:
            print(mensaje)

    # --- DESHABILITADOR DE ATAJOS ---
    def destroy(self):
        """Se ejecuta al cambiar de vista. Limpia los atajos de teclado globales."""
        try:
            self.winfo_toplevel().unbind("<F12>")
            self.winfo_toplevel().unbind("<F11>")
        except Exception:
            pass
        super().destroy()