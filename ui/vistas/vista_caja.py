from bll.gestor_ventas import registrar_venta
from bll.gestor_productos import buscar_producto_por_codigo, buscar_productos_por_nombre
from bll.gestor_caja import *
from ui.componentes.configuracion_componentes import *
from ui.componentes.creador_componentes import *
from ui.modales.modal_cobro import ModalCobro
from ui.modales.modal_cierre import ModalCierre
from ui.vistas.secciones.gestor_carrito import GestorCarrito

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

        self.caja_activa_id = caja_activa.id

        self.frame_principal.grid_columnconfigure(0, weight=8, uniform="grupo1")
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

        # --- INFO DEL CARRITO (TEMPORAL) ---
        lbl_carrito = nuevo_label(self.frame_carrito, "El carrito está vacío", fuente=FUENTE_NEGRITA)
        lbl_carrito.pack(expand=True)

        # --- TEXTO Y BOTONES PANEL DERECHO ---
        self.lbl_texto_total = nuevo_label(frame_totales, "Total:", fuente=FUENTE_TITULOS)
        self.lbl_texto_total.pack(pady=(40, 0))
        
        self.lbl_valor_total = nuevo_label(frame_totales, "$0", fuente=("Arial", 30, "bold"), color_texto=COLOR_EXITO)
        self.lbl_valor_total.pack(pady=(0, 40))

        # --- INICIALIZACION CARRITO ---
        self.gestor_carrito = GestorCarrito(self.frame_carrito, self.lbl_valor_total, self.entry_buscar_prod)
        self.gestor_carrito.actualizar_ui()
        
        self.btn_abrir_cobro = nuevo_boton(
            frame_totales, 
            "Cobrar Venta (F12)", 
            comando=self.abrir_modal_cobro,
            color_fondo=COLOR_EXITO,
            color_hover=COLOR_EXITO_HOVER
        )
        self.btn_abrir_cobro.pack(pady=10)
        self.winfo_toplevel().bind("<F12>", lambda event: self.abrir_modal_cobro())
        
        self.btn_cerrar_caja = nuevo_boton(
            frame_derecho, 
            "Cerrar caja", 
            comando=self.confirmar_cierre_caja,
            color_fondo=COLOR_FALLO,
            color_hover=COLOR_FALLO_HOVER
        )
        self.btn_cerrar_caja.pack(pady=20, padx=20, anchor="se")

    # --- POP-UP COBRO ---
    def abrir_modal_cobro(self):

        # Evitar cobro con el carrito vacio
        if not hasattr(self, 'gestor_carrito') or not self.gestor_carrito.items:
            self.lbl_valor_total.configure(text="¡Vacío!", text_color=COLOR_FALLO)
            self.after(1500, lambda: self.lbl_valor_total.configure(text="$0", text_color=COLOR_EXITO))
            return
        
        total_actual = self.lbl_valor_total.cget("text")
        ModalCobro(self, total_actual, self.procesar_cobro)
    
    # --- POP-UP CIERRE DE CAJA ---    
    def confirmar_cierre_caja(self):
        ModalCierre(self, self.ejecutar_cierre)
    
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
            self.entry_buscar_prod.configure(placeholder_text="¡Producto no encontrado!", placeholder_text_color=COLOR_FALLO)
            self.after(1000, lambda: [self.entry_buscar_prod.configure(placeholder_text="Código de Barras o Nombre...", placeholder_text_color="gray"), self.entry_buscar_prod.focus()])

    def procesar_cobro(self, metodo_pago, modal_referencia):
        """Envía los items guardados en el gestor al BLL."""
        items_carrito = self.gestor_carrito.items
        
        if not items_carrito:
            return

        exito, mensaje = registrar_venta(
            carrito=items_carrito, 
            metodo_pago=metodo_pago, 
            caja_id=self.caja_activa_id
        )

        if exito:
            self.gestor_carrito.vaciar()
            modal_referencia.destroy()
            self.entry_buscar_prod.focus()
            print("¡Venta Exitosa!")
        else:
            print(mensaje)