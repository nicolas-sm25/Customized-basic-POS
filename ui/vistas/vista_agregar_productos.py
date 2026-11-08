import customtkinter as ctk
from bll.gestor_productos import agregar_producto, obtener_productos_unitarios
from ui.vistas.secciones.panel_autocompletado import PanelAutocompletado
from ui.componentes.configuracion_componentes import ConfiguracionComponentes
from ui.componentes.creador_componentes import *

class VistaAgregarProducto(ConfiguracionComponentes):
    def __init__(self, master):
        super().__init__(master)

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.frame_central = nuevo_frame(self, color_fondo="transparent")
        self.frame_central.grid(row=1, column=0)
        
        # --- TÍTULO ---
        self.lbl_titulo = nuevo_label(self.frame_central, "Agregar Producto", fuente=FUENTE_TITULOS)
        self.lbl_titulo.pack(pady=15)

        # --- ENTRADAS DE DATOS BÁSICOS ---
        self.entry_nombre = nueva_caja_texto(self.frame_central, placeholder="Nombre del producto")
        self.entry_nombre.pack(pady=10)
        self.entry_nombre.bind("<Return>", lambda event: self.entry_codigo.focus())
        self.entry_nombre.bind("<Escape>", lambda event: self.cancelar_registro())

        self.entry_codigo = nueva_caja_texto(self.frame_central, placeholder="Código de Barras (Opcional)")
        self.entry_codigo.pack(pady=10)
        self.entry_codigo.bind("<Return>", lambda event: self.entry_costo.focus())
        self.entry_codigo.bind("<Escape>", lambda event: self.cancelar_registro())

        self.entry_costo = nueva_caja_texto(self.frame_central, placeholder="Costo")
        self.entry_costo.pack(pady=10)
        self.entry_costo.bind("<Return>", lambda event: self.entry_precio.focus())
        self.entry_costo.bind("<Escape>", lambda event: self.cancelar_registro())
        self.entry_costo.bind("<KeyRelease>", lambda event: self.formatear_entrada_moneda(self.entry_costo))
        
        self.entry_precio = nueva_caja_texto(self.frame_central, placeholder="Precio de Venta")
        self.entry_precio.pack(pady=10)
        self.entry_precio.bind("<Return>", lambda event: self.entry_stock.focus())
        self.entry_precio.bind("<Escape>", lambda event: self.cancelar_registro())
        self.entry_precio.bind("<KeyRelease>", lambda event: self.formatear_entrada_moneda(self.entry_precio))

        self.entry_stock = nueva_caja_texto(self.frame_central, placeholder="Stock Inicial")
        self.entry_stock.pack(pady=10)
        self.entry_stock.bind("<Return>", self.guardar_producto)
        self.entry_stock.bind("<Escape>", lambda event: self.cancelar_registro())
        self.entry_stock.bind("<KeyRelease>", lambda event: self.formatear_entrada_moneda(self.entry_stock))

        # --- INTERRUPTOR DE RELACIÓN ---
        self.var_paquete = ctk.BooleanVar(value=False)
        self.switch_paquete = ctk.CTkSwitch(
            self.frame_central, 
            text="¿Es un paquete de otro producto?",
            command=self.alternar_paquete,
            variable=self.var_paquete,
            font=("Arial", 12, "bold"),
            progress_color=COLOR_EXITO
        )
        self.switch_paquete.pack(pady=(15, 5))

        # --- PANEL RELACIONAL ---
        self.frame_relacional = nuevo_frame(self.frame_central, color_fondo="#2b2b2b")

        nuevo_label(
            self.frame_relacional, 
            "Busque y seleccione el producto base:", 
            fuente=("Arial", 13, "bold"), 
            color_texto="#ffffff"
        ).pack(pady=(12, 5), padx=20)

        self.entry_base_buscar = nueva_caja_texto(self.frame_relacional, placeholder="Ej: Coca Cola...")
        self.entry_base_buscar.pack(pady=5, padx=20, fill="x")

        self.id_producto_base_seleccionado = None

        nuevo_label(
            self.frame_relacional, 
            "Unidades por paquete:", 
            fuente=("Arial", 13, "bold"), 
            color_texto="#d4ac0d"
        ).pack(pady=(15, 2), padx=20)

        self.entry_cant_paquete = nueva_caja_texto(self.frame_relacional, placeholder="Ej: 30")
        self.entry_cant_paquete.pack(pady=(2, 15), padx=20)

        self.autocompletado_relacional = PanelAutocompletado(self.entry_base_buscar, self.frame_relacional, self.entry_cant_paquete, self.resultado_autocompletado_base)

        # --- BOTONES ---
        self.frame_botones = nuevo_frame(self.frame_central)
        self.frame_botones.pack(pady=20)

        self.btn_guardar = nuevo_boton(self.frame_botones, "Guardar Producto", self.guardar_producto, color_fondo=COLOR_EXITO, color_hover=COLOR_EXITO_HOVER)
        self.btn_guardar.grid(row=0, column=0, padx=10)

        self.btn_cancelar = nuevo_boton(self.frame_botones, "Cancelar", self.cancelar_registro, color_fondo=COLOR_FALLO, color_hover=COLOR_FALLO_HOVER)
        self.btn_cancelar.grid(row=0, column=1, padx=10)
        
        # --- MENSAJE DE ESTADO ---
        self.lbl_mensaje = nuevo_label(self.frame_central, "")
        self.lbl_mensaje.pack(pady=5)
        
        # --- LISTA DE ENTRADAS EDITABLES PARA LIMPIEZA Y BLOQUEO ---
        self.entradas_editables = [
            self.entry_nombre, self.entry_codigo, self.entry_costo, 
            self.entry_precio, self.entry_stock, self.entry_cant_paquete
        ]

    def resultado_autocompletado_base(self, producto):
        """Se activa cuando seleccionan un producto base del menú flotante."""
        self.id_producto_base_seleccionado = producto['id']
        self.entry_base_buscar.delete(0, 'end')
        self.entry_base_buscar.insert(0, producto['nombre'])

        self.entry_base_buscar.configure(state="disabled", fg_color="#1a1a1a", text_color=COLOR_EXITO)
        self.entry_cant_paquete.focus()

    # --- LÓGICA DEL PANEL RELACIONAL ---
    def alternar_paquete(self):
        if self.var_paquete.get():
            self.frame_relacional.pack(fill="x", pady=5, padx=20, before=self.frame_botones)

            self.id_producto_base_seleccionado = None
            self.entry_base_buscar.configure(state="normal", fg_color="#343638", text_color="#ffffff")
            self.entry_base_buscar.delete(0, 'end')

            self.entry_stock.configure(state="normal", fg_color="#343638", text_color="#ffffff")
            self.entry_stock.delete(0, 'end')
            self.entry_stock.configure(placeholder_text="Cantidad de Paquetes")
        else:
            self.frame_relacional.pack_forget()
            self.entry_stock.configure(state="normal", fg_color="#343638", text_color="#ffffff")
            self.entry_stock.delete(0, 'end')
            self.entry_stock.configure(placeholder_text="Stock Inicial")

    # --- AÑADIR PRODUCTO A LA DB ---
    def guardar_producto(self, event=None): 
        nombre = self.entry_nombre.get()
        codigo = self.entry_codigo.get()
        costo_str = self.entry_costo.get().replace(".", "").strip()
        precio_str = self.entry_precio.get().replace(".", "").strip()
        
        es_paquete = self.var_paquete.get()
        stock_str = self.entry_stock.get().replace(".", "").strip()

        if not nombre or not costo_str or not precio_str:
            self.lbl_mensaje.configure(text="Nombre, costo y precio son obligatorios.", text_color="red")
            return

        try:
            costo = float(costo_str)
            precio = float(precio_str)
            stock = int(stock_str) if stock_str else 0
            codigo = codigo if codigo else None

            if costo < 0 or precio < 0 or stock < 0:
                self.lbl_mensaje.configure(text="Los valores numéricos no pueden ser negativos.", text_color="red")
                return
            
            if precio == 0:
                self.lbl_mensaje.configure(text="El precio de venta no puede ser $0.", text_color="red")
                return

            if costo >= precio:
                self.lbl_mensaje.configure(text="El costo no puede ser mayor o igual que el precio de venta.", text_color="red")
                return

            producto_base_id = None
            cantidad_por_paquete = 1

            if es_paquete:
                if not getattr(self, 'id_producto_base_seleccionado', None):
                    self.lbl_mensaje.configure(text="Debe buscar y seleccionar un producto base válido.", text_color="red")
                    return

                producto_base_id = self.id_producto_base_seleccionado
                
                try:
                    cantidad_por_paquete = int(self.entry_cant_paquete.get().replace(".", "").strip())
                    if cantidad_por_paquete <= 1:
                        self.lbl_mensaje.configure(text="La cantidad por paquete debe ser mayor a 1.", text_color="red")
                        return
                except ValueError:
                    self.lbl_mensaje.configure(text="Ingrese una cantidad válida para el paquete.", text_color="red")
                    return

                if stock < 0:
                    self.lbl_mensaje.configure(text="El stock del paquete no puede ser negativo.", text_color="red")
                    return

            exito, mensaje = agregar_producto(
                nombre=nombre, 
                costo=costo, 
                precio_venta=precio, 
                codigo_barras=codigo, 
                stock=stock,
                es_paquete=es_paquete,
                producto_base_id=producto_base_id,
                cantidad_por_paquete=cantidad_por_paquete
            )

            if exito:
                self.lbl_mensaje.configure(text=mensaje, text_color="green")
                if costo == 0:
                    self.lbl_mensaje.configure(text="Advertencia: Producto guardado con costo $0.", text_color="#d4ac0d")
                self.limpiar_campos()
                self.var_paquete.set(False)
                self.alternar_paquete()
                self.entry_nombre.focus()
            else:
                self.lbl_mensaje.configure(text=mensaje, text_color="red")

        except ValueError:
            self.lbl_mensaje.configure(text="Costo, precio y stock deben ser números.", text_color="red")
    
    # --- CANCELAR REGISTRO ---      
    def cancelar_registro(self):
        self.limpiar_campos()
        self.var_paquete.set(False)
        self.alternar_paquete()
        self.lbl_mensaje.configure(text="Registro cancelado.", text_color=COLOR_FALLO)
        self.after(1, self.entry_nombre.focus)