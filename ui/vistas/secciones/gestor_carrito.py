from ui.componentes.creador_componentes import nuevo_frame, nuevo_label, nuevo_boton, nueva_caja_texto
from ui.componentes.creador_componentes import FUENTE_NEGRITA, COLOR_FALLO, COLOR_FALLO_HOVER, COLOR_EXITO

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
            if item["id"] == producto["id"]:
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
        """Redibuja la lista de productos y actualiza el label del total."""
        for widget in self.frame_carrito.winfo_children():
            widget.destroy()

        if not self.items:
            lbl_vacio = nuevo_label(self.frame_carrito, "El carrito está vacío", fuente=FUENTE_NEGRITA)
            lbl_vacio.pack(expand=True)
            self.lbl_total.configure(text="$0")
            return

        total_venta = 0.0
        
        for index, item in enumerate(self.items):
            frame_item = nuevo_frame(self.frame_carrito, color_fondo="#3b3b3b")
            frame_item.pack(fill="x", padx=5, pady=2)
            
            frame_item.grid_columnconfigure(0, weight=1) 
            frame_item.grid_columnconfigure(1, minsize=100) 
            frame_item.grid_columnconfigure(2, minsize=120) 
            
            lbl_nombre = nuevo_label(frame_item, item['nombre'], poscicion="w")
            lbl_nombre.grid(row=0, column=0, sticky="w", padx=10, pady=5)
            
            lbl_precio = nuevo_label(frame_item, f"C. unidad: ${int(item['precio_venta']):,}".replace(",", "."), color_texto="#a0a0a0")
            lbl_precio.grid(row=0, column=1, sticky="e", padx=10, pady=5)
            
            lbl_subtotal = nuevo_label(frame_item, f"Subtotal: ${int(item['subtotal']):,}".replace(",", "."), fuente=FUENTE_NEGRITA, color_texto=COLOR_EXITO)
            lbl_subtotal.grid(row=0, column=2, sticky="e", padx=(10, 20), pady=5)
            
            frame_controles = nuevo_frame(frame_item, color_fondo="transparent")
            frame_controles.grid(row=0, column=3, sticky="e", padx=5, pady=5)

            btn_eliminar = nuevo_boton(frame_controles, "X", comando=lambda i=index: self.eliminar_item(i), color_fondo=COLOR_FALLO, color_hover=COLOR_FALLO_HOVER, ancho=30)
            btn_eliminar.pack(side="right", padx=(10, 0))

            btn_mas = nuevo_boton(frame_controles, "+", comando=lambda i=index: self.cambiar_cantidad(i, 1), ancho=30)
            btn_mas.pack(side="right", padx=2)

            entry_cant = nueva_caja_texto(frame_controles)
            entry_cant.configure(width=50)
            entry_cant.insert(0, str(item['cantidad']))
            entry_cant.pack(side="right", padx=2)
            entry_cant.bind("<Return>", lambda event, i=index, e=entry_cant: self.actualizar_manual(e, i))

            btn_menos = nuevo_boton(frame_controles, "-", comando=lambda i=index: self.cambiar_cantidad(i, -1), ancho=30)
            btn_menos.pack(side="right", padx=2)

            total_venta += item["subtotal"]

        self.lbl_total.configure(text=f"${int(total_venta):,}".replace(",", "."))

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
        self.actualizar_ui()