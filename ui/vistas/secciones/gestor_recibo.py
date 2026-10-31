import customtkinter as ctk
from datetime import datetime
from ui.componentes.creador_componentes import nuevo_frame, nuevo_label, COLOR_EXITO

class GestorRecibo:
    def __init__(self, master_frame):
        self.frame_principal = nuevo_frame(master_frame, color_fondo="#1e1e1e", radio_esquinas=15)
        self.frame_principal.pack(pady=20, fill="both", expand=True, padx=10)
        
        # --- CABECERA ---
        self.lbl_titulo = nuevo_label(self.frame_principal, "RECIBO DE CAJA", fuente=("Arial", 22, "bold"), color_texto="#ffffff")
        self.lbl_titulo.pack(pady=(20, 5))
        
        self.lbl_fecha = nuevo_label(self.frame_principal, "-", color_texto="#a0a0a0", fuente=("Arial", 12))
        self.lbl_fecha.pack(pady=(0, 10))
        
        self.lbl_cliente = nuevo_label(self.frame_principal, "", fuente=("Arial", 14, "bold"), color_texto="#d4ac0d")
        self.lbl_cliente.pack(pady=(0, 10))
        
        # Línea
        nuevo_frame(self.frame_principal, color_fondo="#444444", alto=2).pack(fill="x", padx=15, pady=(0, 5))
        
        # --- LISTA DE PRODUCTOS ---
        self.frame_lista = ctk.CTkScrollableFrame(self.frame_principal, fg_color="transparent")
        self.frame_lista.pack(fill="both", expand=True, padx=5, pady=5)
        
        # --- PIE Y TOTALES ---
        # Línea
        nuevo_frame(self.frame_principal, color_fondo="#444444", alto=2).pack(fill="x", padx=15, pady=(5, 10))
        
        self.frame_totales = nuevo_frame(self.frame_principal, color_fondo="transparent")
        self.frame_totales.pack(fill="x", padx=20, pady=(0, 15))
        
        self.lbl_total = nuevo_label(self.frame_totales, "TOTAL: $0", fuente=("Arial", 24, "bold"), color_texto=COLOR_EXITO, poscicion="e")
        self.lbl_total.pack(anchor="e", pady=(0, 5))
        
        self.lbl_pago_efectivo = nuevo_label(self.frame_totales, "Pago: $0", fuente=("Arial", 14), color_texto="#a0a0a0", poscicion="e")
        self.lbl_pago_efectivo.pack(anchor="e")
        
        self.frame_pago_NEQUI = ctk.CTkFrame(self.frame_totales, fg_color="transparent")
        
        self.lbl_NEQUI_texto1 = nuevo_label(self.frame_pago_NEQUI, "Pagado con ", fuente=("Arial", 14, "bold"), color_texto="#ffffff")
        self.lbl_NEQUI_texto1.pack(side="left")
        
        self.lbl_NEQUI_texto2 = nuevo_label(self.frame_pago_NEQUI, "NEQUI", fuente=("Arial", 20, "bold"), color_texto="#5e17eb")
        self.lbl_NEQUI_texto2.pack(side="left")
        
        self.lbl_cambio = nuevo_label(self.frame_totales, "Cambio: $0", fuente=("Arial", 16, "bold"), color_texto="#d4ac0d", poscicion="e")
        self.lbl_cambio.pack(anchor="e", pady=(5, 0))
        
        self.limpiar_recibo()

    def limpiar_recibo(self):
        self.lbl_fecha.configure(text="Esperando nueva venta...")
        self.lbl_cliente.configure(text="")
        self.lbl_total.configure(text="TOTAL: $0")
        self.frame_pago_NEQUI.pack_forget()
        self.lbl_pago_efectivo.configure(text="")
        self.lbl_cambio.configure(text="")
        for widget in self.frame_lista.winfo_children():
            widget.destroy()

    def actualizar_recibo(self, items, total, metodo_pago, entregado=0, vueltas=0, cliente=None):
        # Configuración Cabecera
        self.lbl_fecha.configure(text=datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        
        if cliente:
            self.lbl_cliente.configure(text=f"Cliente: {cliente}")
            self.lbl_cliente.pack(after=self.lbl_fecha, pady=(0, 10))
        else:
            self.lbl_cliente.configure(text="")
            self.lbl_cliente.pack_forget() # Oculta el espacio si no hay cliente
            
        # Dibujar Items
        for widget in self.frame_lista.winfo_children():
            widget.destroy()
            
        # Títulos de las columnas
        f_enc = nuevo_frame(self.frame_lista, color_fondo="transparent")
        f_enc.pack(fill="x", pady=(0, 10), padx=5)
        
        # Proporciones de columnas
        f_enc.grid_columnconfigure(0, weight=1, uniform="col") # Cantidad
        f_enc.grid_columnconfigure(1, weight=4, uniform="col") # Producto 
        f_enc.grid_columnconfigure(2, weight=3, uniform="col") # C. Unidad
        f_enc.grid_columnconfigure(3, weight=3, uniform="col") # Subtotal
        
        nuevo_label(f_enc, "Cant", fuente=("Arial", 12, "bold"), color_texto="#b0b0b0", poscicion="center").grid(row=0, column=0, sticky="nsew")
        nuevo_label(f_enc, "Producto", fuente=("Arial", 12, "bold"), color_texto="#b0b0b0", poscicion="w").grid(row=0, column=1, sticky="w", padx=5)
        nuevo_label(f_enc, "C. Unidad", fuente=("Arial", 12, "bold"), color_texto="#b0b0b0", poscicion="e").grid(row=0, column=2, sticky="e")
        nuevo_label(f_enc, "Subtotal", fuente=("Arial", 12, "bold"), color_texto="#b0b0b0", poscicion="e").grid(row=0, column=3, sticky="e")

        # Productos
        items_consolidados = {}
        for item in items:
            prod_id = item['id']
            if prod_id in items_consolidados:
                items_consolidados[prod_id]['cantidad'] += item['cantidad']
                items_consolidados[prod_id]['subtotal'] += item['subtotal']
            else:
                items_consolidados[prod_id] = {
                    'nombre': item['nombre'],
                    'cantidad': item['cantidad'],
                    'precio_venta': item['precio_venta'],
                    'subtotal': item['subtotal']
                }

        # Dibujar Productos
        for item in items_consolidados.values():
            f_item = nuevo_frame(self.frame_lista, color_fondo="transparent")
            f_item.pack(fill="x", pady=4, padx=5)
            
            f_item.grid_columnconfigure(0, weight=1, uniform="col")
            f_item.grid_columnconfigure(1, weight=4, uniform="col")
            f_item.grid_columnconfigure(2, weight=3, uniform="col")
            f_item.grid_columnconfigure(3, weight=3, uniform="col")

            nombre_largo = item['nombre']
            nombre_truncado = nombre_largo[:20] + "..." if len(nombre_largo) > 20 else nombre_largo
            
            nuevo_label(f_item, str(item['cantidad']), fuente=("Arial", 13), poscicion="center").grid(row=0, column=0, sticky="nsew")
            nuevo_label(f_item, nombre_truncado, fuente=("Arial", 13), poscicion="w").grid(row=0, column=1, sticky="nsew", padx=5)
            nuevo_label(f_item, f"${int(item['precio_venta']):,}", fuente=("Arial", 12), color_texto="#cccccc").grid(row=0, column=2, sticky="e")
            nuevo_label(f_item, f"${int(item['subtotal']):,}", fuente=("Arial", 13, "bold")).grid(row=0, column=3, sticky="e")
        
        # Totales
        self.lbl_total.configure(text=f"TOTAL: ${int(total):,}".replace(",", "."))
        
        if metodo_pago == "Efectivo":
            self.frame_pago_NEQUI.pack_forget()
            self.lbl_pago_efectivo.pack(anchor="e")
            self.lbl_pago_efectivo.configure(text=f"Efectivo: ${int(entregado):,}".replace(",", "."))
            self.lbl_cambio.configure(text=f"Cambio: ${int(vueltas):,}".replace(",", "."))  
        else:
            self.lbl_pago_efectivo.pack_forget()  
            self.frame_pago_NEQUI.pack(anchor="e", before=self.lbl_cambio)
            self.lbl_cambio.configure(text="")