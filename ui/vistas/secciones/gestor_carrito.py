from ui.componentes.creador_componentes import nuevo_frame, nuevo_label, nuevo_boton, nueva_caja_texto
from ui.componentes.creador_componentes import COLOR_FALLO, COLOR_FALLO_HOVER, COLOR_EXITO

class GestorCarrito:
    """Clase independiente encargada de renderizar y calcular el carrito de compras."""
    def __init__(self, frame_contenedor, lbl_total, entry_buscador):
        self.frame_carrito = frame_contenedor
        self.lbl_total = lbl_total
        self.entry_buscador = entry_buscador
        self.items = []

    def agregar_producto(self, producto):
        """Añade un producto a la lista o suma 1 si ya existe."""
        for item in self.items:
            if item["id"] == producto["id"] and not item.get("recuperado"):
                item["cantidad"] += 1
                item["subtotal"] = item["cantidad"] * item["precio_venta"]
                break
        else:
            self.items.append({
                "id": producto["id"],
                "nombre": producto["nombre"],
                "precio_venta": producto["precio_venta"],
                "costo": producto["costo"],
                "cantidad": 1,
                "subtotal": producto["precio_venta"]
            })
        self.actualizar_ui()

    def actualizar_ui(self):
        """Redibuja la lista de productos como una tabla y actualiza el label del total."""
        for widget in self.frame_carrito.winfo_children():
            widget.destroy()

        if hasattr(self, 'btn_ver_guardadas') and self.btn_ver_guardadas:
            if self.items:
                self.btn_ver_guardadas.configure(state="disabled")
            else:
                self.btn_ver_guardadas.configure(state="normal")

        if not self.items:
            lbl_vacio = nuevo_label(self.frame_carrito, "El carrito está vacío", fuente=("Arial", 16, "bold"))
            lbl_vacio.pack(expand=True)
            self.lbl_total.configure(text="$0")
            return

        # --- CABECERA DE LA TABLA DEL CARRITO ---
        f_enc = nuevo_frame(self.frame_carrito, color_fondo="#1a1a1a")
        f_enc.pack(fill="x", pady=(0, 5), padx=10)
        
        # Proporciones estrictas: Nombre(3), C.U(2), Subt(2), Controles(3)
        f_enc.grid_columnconfigure(0, weight=3, uniform="carr")
        f_enc.grid_columnconfigure(1, weight=2, uniform="carr")
        f_enc.grid_columnconfigure(2, weight=2, uniform="carr")
        f_enc.grid_columnconfigure(3, weight=3, uniform="carr")
        
        nuevo_label(f_enc, "Producto", fuente=("Arial", 14, "bold"), color_texto="#a0a0a0", poscicion="w").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        nuevo_label(f_enc, "C. Unidad", fuente=("Arial", 14, "bold"), color_texto="#a0a0a0", poscicion="e").grid(row=0, column=1, sticky="e")
        nuevo_label(f_enc, "Subtotal", fuente=("Arial", 14, "bold"), color_texto="#a0a0a0", poscicion="e").grid(row=0, column=2, sticky="e")
        nuevo_label(f_enc, "Cantidad / Acciones", fuente=("Arial", 14, "bold"), color_texto="#a0a0a0", poscicion="e").grid(row=0, column=3, sticky="e", padx=10)

        # --- FILAS DE PRODUCTOS ---
        total = 0
        for index, item in enumerate(self.items):
            total += item['subtotal']
            
            # Filas más altas (ipady en el frame o pady en los componentes internos)
            frame_item = nuevo_frame(self.frame_carrito, color_fondo="#2b2b2b")
            frame_item.pack(fill="x", pady=4, padx=10)
            
            frame_item.grid_columnconfigure(0, weight=3, uniform="carr")
            frame_item.grid_columnconfigure(1, weight=2, uniform="carr")
            frame_item.grid_columnconfigure(2, weight=2, uniform="carr")
            frame_item.grid_columnconfigure(3, weight=3, uniform="carr")

            # Textos más grandes (Arial 16)
            lbl_nombre = nuevo_label(frame_item, item['nombre'], fuente=("Arial", 16, "bold"), color_texto="#4fa6ff", poscicion="w")
            lbl_nombre.grid(row=0, column=0, sticky="w", padx=10, pady=10)

            lbl_precio = nuevo_label(frame_item, f"${int(item['precio_venta']):,}".replace(",", "."), fuente=("Arial", 15), color_texto="#cccccc")
            lbl_precio.grid(row=0, column=1, sticky="e", pady=10)

            lbl_subtotal = nuevo_label(frame_item, f"${int(item['subtotal']):,}".replace(",", "."), fuente=("Arial", 16, "bold"), color_texto=COLOR_EXITO)
            lbl_subtotal.grid(row=0, column=2, sticky="e", pady=10)

            # Columna de controles
            frame_controles = nuevo_frame(frame_item, color_fondo="transparent")
            frame_controles.grid(row=0, column=3, sticky="e", padx=10, pady=5)

            if item.get("recuperado"):
                # FIX: Ahora mostramos la cantidad real antes del texto de recuperado
                texto_bloqueado = f"{item['cantidad']} unid. (Recuperado)"
                lbl_bloqueado = nuevo_label(frame_controles, texto_bloqueado, color_texto="#d4ac0d", fuente=("Arial", 14, "bold"))
                lbl_bloqueado.pack(side="right", padx=5)
            else:
                btn_eliminar = nuevo_boton(frame_controles, "X", comando=lambda i=index: self.eliminar_item(i), color_fondo=COLOR_FALLO, color_hover=COLOR_FALLO_HOVER, ancho=40)
                btn_eliminar.pack(side="right", padx=(10, 0))

                btn_mas = nuevo_boton(frame_controles, "+", comando=lambda i=index: self.cambiar_cantidad(i, 1), ancho=40)
                btn_mas.pack(side="right", padx=4)

                # Caja de texto más grande
                entry_cant = nueva_caja_texto(frame_controles)
                entry_cant.configure(width=60, font=("Arial", 16), justify="center")
                entry_cant.insert(0, str(item['cantidad']))
                entry_cant.pack(side="right", padx=4)
                entry_cant.bind("<Return>", lambda event, i=index, e=entry_cant: self.actualizar_manual(e, i))

                btn_menos = nuevo_boton(frame_controles, "-", comando=lambda i=index: self.cambiar_cantidad(i, -1), ancho=40)
                btn_menos.pack(side="right", padx=4)

        # Actualizar total global
        self.lbl_total.configure(text=f"${int(total):,}".replace(",", "."))

    def eliminar_item(self, index):
        self.items.pop(index)
        self.actualizar_ui()

    def cambiar_cantidad(self, index, cambio):
        nueva_cantidad = self.items[index]["cantidad"] + cambio
        if nueva_cantidad > 0:
            self.items[index]["cantidad"] = nueva_cantidad
            self.items[index]["subtotal"] = nueva_cantidad * self.items[index]["precio_venta"]
            self.actualizar_ui()

    def actualizar_manual(self, entry, index):
        valor_str = entry.get().strip()
        try:
            nueva_cantidad = int(valor_str)
            if nueva_cantidad > 0:
                self.items[index]["cantidad"] = nueva_cantidad
                self.items[index]["subtotal"] = nueva_cantidad * self.items[index]["precio_venta"]
        except ValueError:
            pass
        self.actualizar_ui()
        self.entry_buscador.focus()

    def vaciar(self):
        """Limpia el carrito completamente después de una venta."""
        self.items.clear()
        if hasattr(self.frame_carrito.master.master.master, 'cliente_actual'):
            del self.frame_carrito.master.master.master.cliente_actual
        self.actualizar_ui()

    def cargar_items(self, lista_items):
        """Reemplaza el carrito actual con una lista recuperada de la base de datos."""
        for item in lista_items:
            item["recuperado"] = True

        self.items = lista_items
        self.actualizar_ui()