import customtkinter as ctk
from bll.gestor_productos import agregar_producto, buscar_productos_por_nombre
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
        self.lbl_titulo.pack(pady=10)

        # --- ENTRADAS DE DATOS BÁSICOS ---
        self.entry_nombre = nueva_caja_texto(self.frame_central, placeholder="Nombre del producto")
        self.entry_nombre.pack(pady=8)
        self.entry_nombre.bind("<Return>", lambda event: self.entry_codigo.focus())
        self.entry_nombre.bind("<Escape>", lambda event: self.cancelar_registro())

        self.entry_codigo = nueva_caja_texto(self.frame_central, placeholder="Código de Barras (Opcional)")
        self.entry_codigo.pack(pady=8)
        self.entry_codigo.bind("<Return>", lambda event: self.entry_costo.focus())
        self.entry_codigo.bind("<Escape>", lambda event: self.cancelar_registro())

        self.entry_costo = nueva_caja_texto(self.frame_central, placeholder="Costo")
        self.entry_costo.pack(pady=8)
        self.entry_costo.bind("<Return>", lambda event: self.entry_precio.focus())
        self.entry_costo.bind("<Escape>", lambda event: self.cancelar_registro())
        self.entry_costo.bind("<KeyRelease>", lambda event: self.formatear_entrada_moneda(self.entry_costo))
        
        self.entry_precio = nueva_caja_texto(self.frame_central, placeholder="Precio de Venta")
        self.entry_precio.pack(pady=8)
        self.entry_precio.bind("<Return>", self.avanzar_desde_precio)
        self.entry_precio.bind("<Escape>", lambda event: self.cancelar_registro())
        self.entry_precio.bind("<KeyRelease>", lambda event: self.formatear_entrada_moneda(self.entry_precio))

        # --- INTERRUPTOR DE RELACIÓN (ENCIMA DE STOCK) ---
        self.var_paquete = ctk.BooleanVar(value=False)
        self.switch_paquete = ctk.CTkSwitch(
            self.frame_central, 
            text="¿Es un paquete de otro producto?",
            command=self.alternar_paquete,
            variable=self.var_paquete,
            font=("Arial", 12, "bold"),
            progress_color=COLOR_EXITO
        )
        self.switch_paquete.pack(pady=(12, 5))

        # --- PANEL RELACIONAL (OCULTO POR DEFECTO) ---
        self.frame_relacional = nuevo_frame(self.frame_central, color_fondo="#2b2b2b")

        nuevo_label(
            self.frame_relacional, 
            "Busque y seleccione el producto base:", 
            fuente=("Arial", 13, "bold"), 
            color_texto="#ffffff"
        ).pack(pady=(12, 5), padx=20)

        self.entry_base_buscar = nueva_caja_texto(self.frame_relacional, placeholder="Ej: Coca Cola...")
        self.entry_base_buscar.pack(pady=5, padx=20, fill="x")
        self.entry_base_buscar.bind("<Return>", self.confirmar_producto_base)
        self.entry_base_buscar.bind("<Escape>", lambda event: self.cancelar_registro())

        self.lbl_cant_paquete = nuevo_label(
            self.frame_relacional, 
            "Unidades por paquete:", 
            fuente=("Arial", 13, "bold"), 
            color_texto="#d4ac0d"
        )
        self.lbl_cant_paquete.pack(pady=(15, 2), padx=20)

        self.entry_cant_paquete = nueva_caja_texto(self.frame_relacional, placeholder="Ej: 30")
        self.entry_cant_paquete.pack(pady=(2, 15), padx=20)
        self.entry_cant_paquete.bind("<Return>", lambda event: self.entry_stock.focus())
        self.entry_cant_paquete.bind("<Escape>", lambda event: self.cancelar_registro())

        self.autocompletado_relacional = PanelAutocompletado(
            self.entry_base_buscar,
            self.frame_relacional,
            self.lbl_cant_paquete,
            self.resultado_autocompletado_base
        )

        # --- STOCK INICIAL ---
        self.entry_stock = nueva_caja_texto(self.frame_central, placeholder="Stock Inicial")
        self.entry_stock.pack(pady=8)
        self.entry_stock.bind("<Return>", self.guardar_producto)
        self.entry_stock.bind("<Escape>", lambda event: self.cancelar_registro())
        self.entry_stock.bind("<KeyRelease>", lambda event: self.formatear_entrada_moneda(self.entry_stock))

        # --- BOTONES ---
        self.frame_botones = nuevo_frame(self.frame_central)
        self.frame_botones.pack(pady=15)

        self.btn_guardar = nuevo_boton(self.frame_botones, "Guardar Producto", self.guardar_producto, color_fondo=COLOR_EXITO, color_hover=COLOR_EXITO_HOVER)
        self.btn_guardar.grid(row=0, column=0, padx=10)

        self.btn_cancelar = nuevo_boton(self.frame_botones, "Cancelar", self.cancelar_registro, color_fondo=COLOR_FALLO, color_hover=COLOR_FALLO_HOVER)
        self.btn_cancelar.grid(row=0, column=1, padx=10)
        
        # --- MENSAJE DE ESTADO ---
        self.lbl_mensaje = nuevo_label(self.frame_central, "")
        self.lbl_mensaje.pack(pady=5)

        # --- MINI TABLA VISUAL DEL ÚLTIMO PRODUCTO AGREGADO ---
        self.frame_resumen = nuevo_frame(self.frame_central, color_fondo="#202020", radio_esquinas=8)
        
        # --- LISTA DE ENTRADAS EDITABLES PARA LIMPIEZA Y BLOQUEO ---
        self.entradas_editables = [
            self.entry_nombre, self.entry_codigo, self.entry_costo, 
            self.entry_precio, self.entry_base_buscar, self.entry_cant_paquete, self.entry_stock
        ]

    def avanzar_desde_precio(self, event=None):
        """Dirige el foco al buscador de producto base si es paquete, o directo al stock."""
        if self.var_paquete.get():
            self.entry_base_buscar.focus()
        else:
            self.entry_stock.focus()

    def confirmar_producto_base(self, event=None):
        """Selecciona la sugerencia resaltada con Enter o avanza a unidades por paquete."""
        if self.autocompletado_relacional.procesar_enter():
            return
        self.entry_cant_paquete.focus()

    def resultado_autocompletado_base(self, producto):
        """Rellena el nombre sin bloquear el campo y pasa el foco a unidades por paquete."""
        self.entry_base_buscar.delete(0, 'end')
        self.entry_base_buscar.insert(0, producto['nombre'])
        self.entry_cant_paquete.focus()

    def mostrar_mini_tabla(self, nombre, costo, precio, stock, info_paquete=None):
        """Renderiza la mini tabla inferior con los datos del último producto guardado."""
        for w in self.frame_resumen.winfo_children():
            w.destroy()

        self.frame_resumen.pack(pady=(10, 5), padx=20, fill="x")

        nuevo_label(self.frame_resumen, "Último producto registrado:", fuente=("Arial", 11, "bold"), color_texto="#a0a0a0", poscicion="w").pack(fill="x", padx=12, pady=(8, 4))

        tabla = nuevo_frame(self.frame_resumen, color_fondo="#2b2b2b")
        tabla.pack(fill="x", padx=12, pady=(0, 10))
        
        cols = [3, 2, 2, 1, 3] if info_paquete else [3, 2, 2, 1]
        for i, w in enumerate(cols):
            tabla.grid_columnconfigure(i, weight=w, uniform="mini_res")

        headers = [("Nombre", "w"), ("Costo", "e"), ("Precio", "e"), ("Stock", "center")]
        valores = [
            (nombre, "w", "#4fa6ff", "bold"),
            (f"${int(costo):,}".replace(",", "."), "e", "#d4ac0d" if costo == 0 else "#ffffff", "normal"),
            (f"${int(precio):,}".replace(",", "."), "e", COLOR_EXITO, "bold"),
            (str(stock), "center", "#ffffff", "bold")
        ]

        if info_paquete:
            headers.append(("Paquete de", "center"))
            valores.append((info_paquete, "center", "#d4ac0d", "italic"))

        for idx, (h, pos) in enumerate(headers):
            nuevo_label(tabla, h, fuente=("Arial", 11, "bold"), color_texto="#a0a0a0", poscicion=pos).grid(row=0, column=idx, sticky="nsew" if pos=="center" else pos, padx=8, pady=(6, 2))

        for idx, (val, pos, col, peso) in enumerate(valores):
            nuevo_label(tabla, val, fuente=("Arial", 12, peso), color_texto=col, poscicion=pos).grid(row=1, column=idx, sticky="nsew" if pos=="center" else pos, padx=8, pady=(2, 8))

    # --- LÓGICA DEL PANEL RELACIONAL ---
    def alternar_paquete(self):
        self.autocompletado_relacional.ocultar()
        if self.var_paquete.get():
            self.frame_relacional.pack(fill="x", pady=5, padx=20, before=self.entry_stock)
            self.entry_base_buscar.delete(0, 'end')
            self.entry_cant_paquete.delete(0, 'end')
            self.entry_stock.delete(0, 'end')
            self.entry_stock.configure(placeholder_text="Cantidad de Paquetes")
            self.entry_base_buscar.focus()
        else:
            self.frame_relacional.pack_forget()
            self.entry_stock.delete(0, 'end')
            self.entry_stock.configure(placeholder_text="Stock Inicial")

    # --- AÑADIR PRODUCTO A LA DB ---
    def guardar_producto(self, event=None): 
        nombre = self.entry_nombre.get().strip()
        codigo = self.entry_codigo.get().strip()
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
            info_paquete_tabla = None

            if es_paquete:
                texto_base = self.entry_base_buscar.get().strip()
                if not texto_base:
                    self.lbl_mensaje.configure(text="Ingrese el nombre del producto base.", text_color="red")
                    self.entry_base_buscar.focus()
                    return

                resultados = buscar_productos_por_nombre(texto_base)
                producto_base = next(
                    (p for p in resultados if p.get('activo', True) and p['nombre'].strip().lower() == texto_base.lower()),
                    None
                )

                if not producto_base:
                    self.lbl_mensaje.configure(text=f"El producto base '{texto_base}' no existe en la base de datos.", text_color="red")
                    self.entry_base_buscar.focus()
                    return

                producto_base_id = producto_base['id']
                
                try:
                    cantidad_por_paquete = int(self.entry_cant_paquete.get().replace(".", "").strip())
                    if cantidad_por_paquete <= 1:
                        self.lbl_mensaje.configure(text="La cantidad por paquete debe ser mayor a 1.", text_color="red")
                        self.entry_cant_paquete.focus()
                        return
                except ValueError:
                    self.lbl_mensaje.configure(text="Ingrese una cantidad válida para el paquete.", text_color="red")
                    self.entry_cant_paquete.focus()
                    return

                info_paquete_tabla = f"{producto_base['nombre']} (x{cantidad_por_paquete})"

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
                self.autocompletado_relacional.ocultar()
                self.lbl_mensaje.configure(text=mensaje, text_color="green")
                if costo == 0:
                    self.lbl_mensaje.configure(text="Advertencia: Producto guardado con costo $0.", text_color="#d4ac0d")
                
                self.mostrar_mini_tabla(nombre, costo, precio, stock, info_paquete_tabla)

                self.limpiar_campos()
                self.var_paquete.set(False)
                self.alternar_paquete()
                self.entry_nombre.focus()
            
            ventana_ppal = self.winfo_toplevel()
            if hasattr(ventana_ppal, "actualizar_contador_notificaciones"):
                ventana_ppal.actualizar_contador_notificaciones()

            else:
                self.lbl_mensaje.configure(text=mensaje, text_color="red")

        except ValueError:
            self.lbl_mensaje.configure(text="Costo, precio y stock deben ser números.", text_color="red")
    
    # --- CANCELAR REGISTRO ---      
    def cancelar_registro(self):
        self.autocompletado_relacional.ocultar()
        self.limpiar_campos()
        self.var_paquete.set(False)
        self.alternar_paquete()
        self.lbl_mensaje.configure(text="Registro cancelado.", text_color=COLOR_FALLO)
        self.after(1, self.entry_nombre.focus)