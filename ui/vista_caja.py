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
        self.frame_principal.grid_columnconfigure(0, weight=3)
        self.frame_principal.grid_columnconfigure(1, weight=1)
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
        # self.entry_buscar_prod.bind("<Return>", self.agregar_al_carrito) ---> Se implementa luego
        
        self.btn_agregar = nuevo_boton(frame_busqueda, "Agregar", comando=lambda: print("Buscar y agregar"))
        self.btn_agregar.pack(side="right")

        # --- INFO DEL CARRITO (TEMPORAL) ---
        lbl_carrito = nuevo_label(self.frame_carrito, "El carrito está vacío", fuente=FUENTE_NEGRITA)
        lbl_carrito.pack(expand=True)

        # --- TEXTO Y BOTONES PANEL DERECHO ---
        self.lbl_texto_total = nuevo_label(frame_totales, "Total:", fuente=FUENTE_TITULOS)
        self.lbl_texto_total.pack(pady=(40, 0))
        
        self.lbl_valor_total = nuevo_label(frame_totales, "$0", fuente=("Arial", 40, "bold"), color_texto=COLOR_EXITO)
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

        #! Lógica para evitar cobro con el carrito vacio
        # if not hasattr(self, 'carrito') or not self.carrito:
        #    self.lbl_valor_total.configure(text="¡Vacío!", text_color=COLOR_FALLO)
        #    self.after(1500, lambda: self.lbl_valor_total.configure(text="$0", text_color=COLOR_EXITO))
        #    return
        
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