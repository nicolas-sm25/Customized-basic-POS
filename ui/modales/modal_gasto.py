import customtkinter as ctk
from ui.componentes.creador_componentes import *
from ui.vistas.secciones.panel_autocompletado import PanelAutocompletado
from bll.gestor_productos import buscar_producto_por_codigo, buscar_productos_por_nombre
from bll.gestor_caja import registrar_gasto, registrar_mermas_lote

class ModalGasto:
    def __init__(self, master, caja_id, callback_confirmar):
        self.master = master
        self.caja_id = caja_id
        self.callback_confirmar = callback_confirmar
        self.items_merma = []

        self.modal = nuevo_modal(master, "Registrar Gasto", 720, 580)

        self.frame_modal = nuevo_frame(self.modal)
        self.frame_modal.pack(expand=True, fill="both", padx=20, pady=15)

        nuevo_label(self.frame_modal, "Registrar Salida", fuente=FUENTE_TITULOS).pack(pady=(0, 10))

        # --- SELECTOR DE MODO ---
        self.var_tipo = ctk.StringVar(value="Inventario")
        frame_radios = nuevo_frame(self.frame_modal, color_fondo="#2b2b2b", radio_esquinas=8)
        frame_radios.pack(fill="x", padx=10, pady=(0, 10))

        ctk.CTkRadioButton(
            frame_radios, text="Baja de Productos", variable=self.var_tipo, value="Inventario",
            command=self.redibujar_contenido, font=("Arial", 13, "bold"), text_color="#d4ac0d"
        ).pack(side="left", expand=True, pady=10)

        ctk.CTkRadioButton(
            frame_radios, text="Salida de Dinero", variable=self.var_tipo, value="Dinero",
            command=self.redibujar_contenido, font=("Arial", 13, "bold"), text_color="#ffffff"
        ).pack(side="right", expand=True, pady=10)

        # --- CONTENEDOR ---
        self.frame_contenido = nuevo_frame(self.frame_modal, color_fondo="transparent")
        self.frame_contenido.pack(expand=True, fill="both")

        self.modal.bind("<Escape>", lambda e: self.cerrar_modal())
        self.redibujar_contenido()

    def redibujar_contenido(self):
        """Limpia y vuelve a dibujar todo el formulario según el modo seleccionado."""
        for widget in self.frame_contenido.winfo_children():
            widget.destroy()

        if self.var_tipo.get() == "Inventario":
            self.modal.geometry("720x600")
            self.dibujar_modo_merma()
        else:
            self.modal.geometry("460x350")
            self.dibujar_modo_dinero()

    # BAJA DE PRODUCTOS
    def dibujar_modo_merma(self):
        frame_busqueda = nuevo_frame(self.frame_contenido, color_fondo="transparent")
        frame_busqueda.pack(fill="x", padx=10, pady=(0, 8))

        self.entry_prod = nueva_caja_texto(frame_busqueda, placeholder="Código, Nombre o Cant*Producto...")
        self.entry_prod.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.entry_prod.bind("<Return>", self.agregar_a_merma)
        self.entry_prod.bind("<Escape>", lambda e: self.cerrar_modal())

        nuevo_boton(frame_busqueda, "Agregar", comando=self.agregar_a_merma, ancho=100).pack(side="right")

        self.frame_carrito_merma = nuevo_frame(self.frame_contenido, color_fondo="#202020", radio_esquinas=8)
        self.frame_carrito_merma.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.autocompletado = PanelAutocompletado(
            self.entry_prod,
            self.frame_contenido,
            self.frame_carrito_merma,
            self.resultado_autocompletado_merma
        )

        frame_inf = nuevo_frame(self.frame_contenido, color_fondo="transparent")
        frame_inf.pack(fill="x", padx=10)

        self.lbl_total_merma = nuevo_label(frame_inf, "Costo total perdido: $0", fuente=("Arial", 14, "bold"), color_texto="#d4ac0d", poscicion="e")
        self.lbl_total_merma.pack(fill="x", pady=(0, 8))

        self.entry_desc = nueva_caja_texto(frame_inf, placeholder="Descripción (Ej: Daño, vencimiento, autoconsumo...)")
        self.entry_desc.pack(fill="x", pady=(0, 8))
        self.entry_desc.bind("<Return>", lambda e: self.procesar_mermas())
        self.entry_desc.bind("<Escape>", lambda e: self.cerrar_modal())

        self.lbl_mensaje = nuevo_label(frame_inf, "")
        self.lbl_mensaje.pack(pady=2)

        frame_botones = nuevo_frame(frame_inf, color_fondo="transparent")
        frame_botones.pack(pady=8)

        nuevo_boton(frame_botones, "Registrar Baja", comando=self.procesar_mermas, color_fondo=COLOR_EXITO, color_hover=COLOR_EXITO_HOVER).grid(row=0, column=0, padx=10)
        nuevo_boton(frame_botones, "Cancelar (Esc)", comando=self.cerrar_modal, color_fondo=COLOR_FALLO, color_hover=COLOR_FALLO_HOVER).grid(row=0, column=1, padx=10)

        self.actualizar_ui_merma()
        self.modal.after(50, self.entry_prod.focus)

    def resultado_autocompletado_merma(self, producto):
        criterio = self.entry_prod.get().strip()
        cantidad = 1
        if "*" in criterio:
            partes = criterio.split("*", 1)
            if partes[0].isdigit() and int(partes[0]) > 0:
                cantidad = int(partes[0])
        self.agregar_item_lista(producto, cantidad)

    def agregar_a_merma(self, event=None):
        if self.autocompletado.procesar_enter():
            return

        criterio = self.entry_prod.get().strip()
        if not criterio:
            return

        cantidad = 1
        if "*" in criterio:
            partes = criterio.split("*", 1)
            if partes[0].isdigit():
                cantidad = int(partes[0])
                if cantidad <= 0:
                    cantidad = 1
                criterio = partes[1].strip()

        producto = buscar_producto_por_codigo(criterio)
        if not producto:
            resultados = buscar_productos_por_nombre(criterio)
            if resultados:
                producto = next((p for p in resultados if p['nombre'].lower() == criterio.lower()), resultados[0])

        self.agregar_item_lista(producto, cantidad)

    def agregar_item_lista(self, producto, cantidad=1):
        if not producto:
            self.entry_prod.delete(0, 'end')
            self.lbl_mensaje.configure(text="Producto no encontrado.", text_color=COLOR_FALLO)
            self.entry_prod.focus()
            return

        if not producto.get('activo', True):
            self.entry_prod.delete(0, 'end')
            self.lbl_mensaje.configure(text="El producto está inhabilitado.", text_color="#d4ac0d")
            self.entry_prod.focus()
            return

        self.lbl_mensaje.configure(text="")
        for item in self.items_merma:
            if item["id"] == producto["id"]:
                item["cantidad"] += cantidad
                item["subtotal"] = item["cantidad"] * item["costo"]
                self.entry_prod.delete(0, 'end')
                self.actualizar_ui_merma()
                self.entry_prod.focus()
                return

        self.items_merma.append({
            "id": producto["id"],
            "nombre": producto["nombre"],
            "costo": producto.get("costo", 0),
            "cantidad": cantidad,
            "subtotal": cantidad * producto.get("costo", 0)
        })
        self.entry_prod.delete(0, 'end')
        self.actualizar_ui_merma()
        self.entry_prod.focus()

    def actualizar_ui_merma(self):
        for widget in self.frame_carrito_merma.winfo_children():
            widget.destroy()

        if not self.items_merma:
            nuevo_label(self.frame_carrito_merma, "Agrega productos para dar de baja del inventario", fuente=("Arial", 13, "bold"), color_texto="#a0a0a0").pack(expand=True, pady=40)
            self.lbl_total_merma.configure(text="Costo total perdido: $0")
            return

        scroll = ctk.CTkScrollableFrame(self.frame_carrito_merma, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=5, pady=5)

        # Cabecera
        f_enc = nuevo_frame(scroll, color_fondo="#1a1a1a")
        f_enc.pack(fill="x", pady=(0, 5))
        f_enc.grid_columnconfigure(0, weight=3, uniform="merma")
        f_enc.grid_columnconfigure(1, weight=2, uniform="merma")
        f_enc.grid_columnconfigure(2, weight=2, uniform="merma")
        f_enc.grid_columnconfigure(3, weight=3, uniform="merma")

        nuevo_label(f_enc, "Producto", fuente=("Arial", 12, "bold"), color_texto="#a0a0a0", poscicion="w").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        nuevo_label(f_enc, "Costo U.", fuente=("Arial", 12, "bold"), color_texto="#a0a0a0", poscicion="e").grid(row=0, column=1, sticky="e")
        nuevo_label(f_enc, "Subtotal", fuente=("Arial", 12, "bold"), color_texto="#a0a0a0", poscicion="e").grid(row=0, column=2, sticky="e")
        nuevo_label(f_enc, "Cantidad", fuente=("Arial", 12, "bold"), color_texto="#a0a0a0", poscicion="e").grid(row=0, column=3, sticky="e", padx=10)

        total_costo = 0
        for index, item in enumerate(self.items_merma):
            total_costo += item["subtotal"]

            frame_item = nuevo_frame(scroll, color_fondo="#2b2b2b")
            frame_item.pack(fill="x", pady=3)
            frame_item.grid_columnconfigure(0, weight=3, uniform="merma")
            frame_item.grid_columnconfigure(1, weight=2, uniform="merma")
            frame_item.grid_columnconfigure(2, weight=2, uniform="merma")
            frame_item.grid_columnconfigure(3, weight=3, uniform="merma")

            nuevo_label(frame_item, item["nombre"], fuente=("Arial", 13, "bold"), color_texto="#4fa6ff", poscicion="w").grid(row=0, column=0, sticky="w", padx=10, pady=8)
            nuevo_label(frame_item, f"${int(item['costo']):,}".replace(",", "."), fuente=("Arial", 12), color_texto="#cccccc").grid(row=0, column=1, sticky="e", pady=8)

            lbl_sub = nuevo_label(frame_item, f"${int(item['subtotal']):,}".replace(",", "."), fuente=("Arial", 13, "bold"), color_texto=COLOR_FALLO)
            lbl_sub.grid(row=0, column=2, sticky="e", pady=8)

            frame_controles = nuevo_frame(frame_item, color_fondo="transparent")
            frame_controles.grid(row=0, column=3, sticky="e", padx=8, pady=4)

            nuevo_boton(frame_controles, "X", comando=lambda i=index: self.eliminar_item_merma(i), color_fondo=COLOR_FALLO, color_hover=COLOR_FALLO_HOVER, ancho=32).pack(side="right", padx=(6, 0))
            nuevo_boton(frame_controles, "+", comando=lambda i=index: self.cambiar_cantidad_merma(i, 1), ancho=32).pack(side="right", padx=3)

            entry_cant = nueva_caja_texto(frame_controles)
            entry_cant.configure(width=50, font=("Arial", 13), justify="center")
            entry_cant.insert(0, str(item["cantidad"]))
            entry_cant.pack(side="right", padx=3)

            entry_cant.bind("<Return>", lambda e, i=index, ent=entry_cant: self.actualizar_manual_merma(ent, i))
            entry_cant.bind("<KeyRelease>", lambda e, i=index, ent=entry_cant, lbl_s=lbl_sub: self.actualizar_silencioso_merma(ent, i, lbl_s))

            nuevo_boton(frame_controles, "-", comando=lambda i=index: self.cambiar_cantidad_merma(i, -1), ancho=32).pack(side="right", padx=3)

        self.lbl_total_merma.configure(text=f"Costo total perdido: ${int(total_costo):,}".replace(",", "."))

    def eliminar_item_merma(self, index):
        self.items_merma.pop(index)
        self.actualizar_ui_merma()

    def cambiar_cantidad_merma(self, index, cambio):
        nueva = self.items_merma[index]["cantidad"] + cambio
        if nueva > 0:
            self.items_merma[index]["cantidad"] = nueva
            self.items_merma[index]["subtotal"] = nueva * self.items_merma[index]["costo"]
            self.actualizar_ui_merma()

    def actualizar_manual_merma(self, entry, index):
        valor_str = entry.get().strip()
        if valor_str.isdigit() and int(valor_str) > 0:
            self.items_merma[index]["cantidad"] = int(valor_str)
            self.items_merma[index]["subtotal"] = int(valor_str) * self.items_merma[index]["costo"]
        self.actualizar_ui_merma()
        self.entry_prod.focus()

    def actualizar_silencioso_merma(self, entry, index, lbl_sub):
        valor_str = entry.get().strip()
        if not valor_str.isdigit() or int(valor_str) <= 0:
            return
        nueva = int(valor_str)
        self.items_merma[index]["cantidad"] = nueva
        self.items_merma[index]["subtotal"] = nueva * self.items_merma[index]["costo"]
        lbl_sub.configure(text=f"${int(self.items_merma[index]['subtotal']):,}".replace(",", "."))

        total_costo = sum(it["subtotal"] for it in self.items_merma)
        self.lbl_total_merma.configure(text=f"Costo total perdido: ${int(total_costo):,}".replace(",", "."))

    def procesar_mermas(self):
        if not self.items_merma:
            self.lbl_mensaje.configure(text="Agregue al menos un producto a la lista.", text_color=COLOR_FALLO)
            return

        desc = self.entry_desc.get().strip()
        if not desc:
            self.lbl_mensaje.configure(text="Ingrese una descripción o motivo de la baja.", text_color=COLOR_FALLO)
            self.entry_desc.focus()
            return

        exito, msj = registrar_mermas_lote(self.caja_id, desc, self.items_merma)
        self.cerrar_modal()
        self.callback_confirmar(exito, msj)

    # SALIDA DE DINERO
    def dibujar_modo_dinero(self):
        self.entry_desc = nueva_caja_texto(self.frame_contenido, placeholder="Descripción (Ej: Pago a proveedor)")
        self.entry_desc.pack(pady=10, fill="x", padx=20)

        self.entry_monto = nueva_caja_texto(self.frame_contenido, placeholder="Monto del gasto ($)")
        self.entry_monto.pack(pady=10, fill="x", padx=20)

        self.lbl_mensaje = nuevo_label(self.frame_contenido, "")
        self.lbl_mensaje.pack(pady=5)

        frame_botones = nuevo_frame(self.frame_contenido, color_fondo="transparent")
        frame_botones.pack(pady=10)

        nuevo_boton(frame_botones, "Guardar (Enter)", comando=self.procesar_gasto_dinero, color_fondo=COLOR_EXITO, color_hover=COLOR_EXITO_HOVER).grid(row=0, column=0, padx=10)
        nuevo_boton(frame_botones, "Cancelar (Esc)", comando=self.cerrar_modal, color_fondo=COLOR_FALLO, color_hover=COLOR_FALLO_HOVER).grid(row=0, column=1, padx=10)

        self.entry_monto.bind("<KeyRelease>", self.formatear_moneda)
        self.entry_desc.bind("<Return>", lambda e: self.entry_monto.focus())
        self.entry_monto.bind("<Return>", lambda e: self.procesar_gasto_dinero())
        self.entry_desc.bind("<Escape>", lambda e: self.cerrar_modal())
        self.entry_monto.bind("<Escape>", lambda e: self.cerrar_modal())

        self.modal.after(50, self.entry_desc.focus)

    def formatear_moneda(self, event=None):
        texto_limpio = ''.join(filter(str.isdigit, self.entry_monto.get().replace(".", "")))
        self.entry_monto.delete(0, 'end')
        if texto_limpio:
            self.entry_monto.insert(0, f"{int(texto_limpio):,}".replace(",", "."))

    def procesar_gasto_dinero(self):
        desc = self.entry_desc.get().strip()
        monto_str = self.entry_monto.get().replace(".", "").strip()

        if not desc or not monto_str:
            self.lbl_mensaje.configure(text="Ingrese descripción y monto.", text_color=COLOR_FALLO)
            return
        try:
            monto = float(monto_str)
            if monto <= 0:
                self.lbl_mensaje.configure(text="El monto debe ser mayor a $0.", text_color=COLOR_FALLO)
                return
            exito, msj = registrar_gasto(self.caja_id, desc, monto, tipo_gasto="Dinero")
            self.cerrar_modal()
            self.callback_confirmar(exito, msj)
        except ValueError:
            self.lbl_mensaje.configure(text="Monto inválido.", text_color=COLOR_FALLO)

    def cerrar_modal(self):
        self.master.focus()
        self.modal.destroy()
        if hasattr(self.master, 'entry_buscar_prod'):
            self.master.after(2001, self.master.entry_buscar_prod.focus)