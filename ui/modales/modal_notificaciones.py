import customtkinter as ctk
from ui.componentes.creador_componentes import *
from bll.gestor_notificaciones import (
    obtener_notificaciones,
    reactivar_notificacion
)
from bll.gestor_productos import (
    obtener_producto_por_id,
    sumar_stock_rapido,
    actualizar_costo_rapido,
    obtener_inventario_completo,
    reactivar_producto_db
)


class ModalNotificacionesIgnoradas:
    """Modal para consultar notificaciones ignoradas y reactivarlas."""
    def __init__(self, master, callback_actualizar):
        self.modal = nuevo_modal(master, "Notificaciones Ignoradas", 860, 560)
        self.modal.focus_force()
        self.callback_actualizar = callback_actualizar

        frame_ppal = nuevo_frame(self.modal)
        frame_ppal.pack(expand=True, fill="both", padx=20, pady=15)

        nuevo_label(frame_ppal, "Notificaciones Ignoradas", fuente=FUENTE_TITULOS).pack(pady=(0, 10))

        self.scroll = ctk.CTkScrollableFrame(frame_ppal, fg_color="#202020")
        self.scroll.pack(fill="both", expand=True, pady=5)

        self.renderizar()

        nuevo_boton(
            frame_ppal, "Cerrar (Esc)",
            comando=self.modal.destroy,
            color_fondo=COLOR_FALLO,
            color_hover=COLOR_FALLO_HOVER,
            ancho=140
        ).pack(pady=(10, 0))
        self.modal.bind("<Escape>", lambda e: self.modal.destroy())

    def renderizar(self):
        for w in self.scroll.winfo_children():
            w.destroy()

        ignoradas = obtener_notificaciones(estado="Ignorada")
        if not ignoradas:
            nuevo_label(
                self.scroll,
                "No hay notificaciones ignoradas actualmente.",
                fuente=("Arial", 14, "bold"),
                color_texto="#a0a0a0"
            ).pack(pady=60)
            return

        for n in ignoradas:
            card = nuevo_frame(self.scroll, color_fondo="#2b2b2b", radio_esquinas=8)
            card.pack(fill="x", pady=5, padx=8)
            card.grid_columnconfigure(0, weight=1)

            f_info = nuevo_frame(card, color_fondo="transparent")
            f_info.grid(row=0, column=0, sticky="w", padx=12, pady=10)

            nuevo_label(
                f_info,
                f"[{n['etiqueta_tipo']}]  •  Ignorada por {n['ignorada_por'] or 'Desconocido'} ({n['fecha_ignorada'] or 'N/A'})",
                fuente=("Arial", 11, "bold"),
                color_texto="#d4ac0d",
                poscicion="w"
            ).pack(anchor="w")

            lbl_desc = nuevo_label(f_info, n["descripcion"], fuente=("Arial", 12), color_texto="#ffffff", poscicion="w")
            lbl_desc.configure(wraplength=580, justify="left")
            lbl_desc.pack(anchor="w", pady=(3, 0))

            nuevo_boton(
                card,
                "Reactivar",
                comando=lambda nid=n["id"]: self.ejecutar_reactivacion(nid),
                color_fondo="#1f538d",
                color_hover="#14375e",
                ancho=110
            ).grid(row=0, column=1, padx=12, pady=10)

    def ejecutar_reactivacion(self, notif_id):
        if reactivar_notificacion(notif_id):
            self.renderizar()
            self.callback_actualizar()


class ModalAccionStock:
    """Mini-modal para sumar unidades a un producto con stock agotado o negativo."""
    def __init__(self, master, producto_id, callback_actualizar):
        self.producto = obtener_producto_por_id(producto_id)
        self.callback_actualizar = callback_actualizar

        self.modal = nuevo_modal(master, "Añadir Stock al Producto", 440, 310)
        self.modal.focus_force()

        frame = nuevo_frame(self.modal)
        frame.pack(expand=True, fill="both", padx=25, pady=20)

        nuevo_label(frame, "Añadir Stock", fuente=FUENTE_TITULOS).pack(pady=(0, 10))

        if not self.producto:
            nuevo_label(frame, "No se encontró el producto.", color_texto=COLOR_FALLO).pack(pady=20)
            nuevo_boton(frame, "Cerrar", comando=self.modal.destroy, color_fondo=COLOR_FALLO).pack()
            return

        nuevo_label(
            frame,
            self.producto["nombre"],
            fuente=("Arial", 14, "bold"),
            color_texto="#4fa6ff"
        ).pack(pady=(0, 4))

        stock_actual = self.producto["stock"]
        nuevo_label(
            frame,
            f"Stock actual en sistema: {stock_actual} uds",
            fuente=("Arial", 12, "bold"),
            color_texto=COLOR_FALLO if stock_actual <= 0 else "#a0a0a0"
        ).pack(pady=(0, 12))

        nuevo_label(frame, "Unidades a ingresar:", fuente=("Arial", 12)).pack(pady=(0, 5))
        self.entry_cantidad = nueva_caja_texto(frame, placeholder="Ej: 12", ancho=180)
        self.entry_cantidad.pack(pady=5)
        self.entry_cantidad.bind("<Return>", lambda e: self.guardar())
        self.modal.after(50, self.entry_cantidad.focus)

        self.lbl_error = nuevo_label(frame, "", fuente=("Arial", 11, "bold"), color_texto=COLOR_FALLO)
        self.lbl_error.pack(pady=5)

        f_btns = nuevo_frame(frame, color_fondo="transparent")
        f_btns.pack(pady=(8, 0))

        nuevo_boton(
            f_btns, "Guardar",
            comando=self.guardar,
            color_fondo=COLOR_EXITO,
            color_hover=COLOR_EXITO_HOVER,
            ancho=130
        ).pack(side="left", padx=8)

        nuevo_boton(
            f_btns, "Cancelar",
            comando=self.modal.destroy,
            color_fondo=COLOR_FALLO,
            color_hover=COLOR_FALLO_HOVER,
            ancho=130
        ).pack(side="left", padx=8)

        self.modal.bind("<Escape>", lambda e: self.modal.destroy())

    def guardar(self):
        valor = self.entry_cantidad.get().strip()
        if not valor.isdigit() or int(valor) <= 0:
            self.lbl_error.configure(text="Ingresa una cantidad entera mayor a 0.")
            return

        exito, msg = sumar_stock_rapido(self.producto["id"], int(valor))
        if exito:
            self.modal.destroy()
            self.callback_actualizar()
        else:
            self.lbl_error.configure(text=msg)


class ModalAccionCosto:
    """Mini-modal exclusivo para Administrador para corregir un producto con costo $0."""
    def __init__(self, master, producto_id, es_admin, callback_actualizar):
        self.producto = obtener_producto_por_id(producto_id)
        self.es_admin = es_admin
        self.callback_actualizar = callback_actualizar

        self.modal = nuevo_modal(master, "Editar Costo de Producto", 450, 320)
        self.modal.focus_force()

        frame = nuevo_frame(self.modal)
        frame.pack(expand=True, fill="both", padx=25, pady=20)

        nuevo_label(frame, "Corregir Costo ($0)", fuente=FUENTE_TITULOS).pack(pady=(0, 10))

        if not self.es_admin:
            nuevo_label(
                frame,
                "Acceso restringido: solo un Administrador\npuede modificar el costo de los productos.",
                fuente=("Arial", 13, "bold"),
                color_texto=COLOR_FALLO
            ).pack(pady=30)
            nuevo_boton(frame, "Cerrar", comando=self.modal.destroy, color_fondo=COLOR_FALLO, ancho=140).pack()
            self.modal.bind("<Escape>", lambda e: self.modal.destroy())
            return

        if not self.producto:
            nuevo_label(frame, "No se encontró el producto.", color_texto=COLOR_FALLO).pack(pady=20)
            nuevo_boton(frame, "Cerrar", comando=self.modal.destroy, color_fondo=COLOR_FALLO).pack()
            return

        nuevo_label(
            frame,
            self.producto["nombre"],
            fuente=("Arial", 14, "bold"),
            color_texto="#4fa6ff"
        ).pack(pady=(0, 4))

        precio_fmt = f"${int(self.producto['precio_venta']):,}".replace(",", ".")
        nuevo_label(
            frame,
            f"Precio de venta actual: {precio_fmt}",
            fuente=("Arial", 12),
            color_texto="#d4ac0d"
        ).pack(pady=(0, 12))

        nuevo_label(frame, "Nuevo costo unitario ($):", fuente=("Arial", 12)).pack(pady=(0, 5))
        self.entry_costo = nueva_caja_texto(frame, placeholder="Ej: 1500", ancho=180)
        self.entry_costo.pack(pady=5)
        self.entry_costo.bind("<KeyRelease>", self.formatear_moneda)
        self.entry_costo.bind("<Return>", lambda e: self.guardar())
        self.modal.after(50, self.entry_costo.focus)

        self.lbl_error = nuevo_label(frame, "", fuente=("Arial", 11, "bold"), color_texto=COLOR_FALLO)
        self.lbl_error.pack(pady=5)

        f_btns = nuevo_frame(frame, color_fondo="transparent")
        f_btns.pack(pady=(8, 0))

        nuevo_boton(
            f_btns, "Guardar Costo",
            comando=self.guardar,
            color_fondo=COLOR_EXITO,
            color_hover=COLOR_EXITO_HOVER,
            ancho=140
        ).pack(side="left", padx=8)

        nuevo_boton(
            f_btns, "Cancelar",
            comando=self.modal.destroy,
            color_fondo=COLOR_FALLO,
            color_hover=COLOR_FALLO_HOVER,
            ancho=130
        ).pack(side="left", padx=8)

        self.modal.bind("<Escape>", lambda e: self.modal.destroy())

    def formatear_moneda(self, event=None):
        texto = self.entry_costo.get().replace(".", "").strip()
        if texto.isdigit():
            formateado = f"{int(texto):,}".replace(",", ".")
            self.entry_costo.delete(0, "end")
            self.entry_costo.insert(0, formateado)

    def guardar(self):
        limpio = self.entry_costo.get().replace(".", "").strip()
        if not limpio.isdigit() or float(limpio) <= 0:
            self.lbl_error.configure(text="Ingresa un costo válido mayor a $0.")
            return

        exito, msg = actualizar_costo_rapido(self.producto["id"], float(limpio))
        if exito:
            self.modal.destroy()
            self.callback_actualizar()
        else:
            self.lbl_error.configure(text=msg)


class ModalProductosInactivosNotif:
    """Muestra los productos inactivos resaltando con borde el producto base requerido por un paquete activo."""
    def __init__(self, master, paquete_id, callback_actualizar):
        self.paquete = obtener_producto_por_id(paquete_id)
        self.base_resaltada_id = self.paquete.get("producto_base_id") if self.paquete else None
        self.callback_actualizar = callback_actualizar

        self.modal = nuevo_modal(master, "Productos Inactivos", 780, 520)
        self.modal.focus_force()

        frame_ppal = nuevo_frame(self.modal)
        frame_ppal.pack(expand=True, fill="both", padx=20, pady=15)

        nuevo_label(frame_ppal, "Productos Inactivos", fuente=FUENTE_TITULOS).pack(pady=(0, 5))

        if self.paquete:
            nuevo_label(
                frame_ppal,
                f"El paquete '{self.paquete['nombre']}' está activo y requiere reactivar su producto base resaltado:",
                fuente=("Arial", 12, "bold"),
                color_texto="#d4ac0d"
            ).pack(pady=(0, 10))

        self.scroll = ctk.CTkScrollableFrame(frame_ppal, fg_color="#202020")
        self.scroll.pack(fill="both", expand=True, pady=5)

        self.renderizar()

        nuevo_boton(
            frame_ppal, "Cerrar (Esc)",
            comando=self.modal.destroy,
            color_fondo=COLOR_FALLO,
            color_hover=COLOR_FALLO_HOVER,
            ancho=140
        ).pack(pady=(10, 0))
        self.modal.bind("<Escape>", lambda e: self.modal.destroy())

    def renderizar(self):
        for w in self.scroll.winfo_children():
            w.destroy()

        todos = obtener_inventario_completo()
        inactivos = [p for p in todos if not p["activo"]]

        # Poner el producto base resaltado primero
        inactivos.sort(key=lambda p: 0 if p["id"] == self.base_resaltada_id else 1)

        if not inactivos:
            nuevo_label(
                self.scroll,
                "No hay productos inactivos actualmente.",
                fuente=("Arial", 14, "bold"),
                color_texto=COLOR_EXITO
            ).pack(pady=60)
            return

        for p in inactivos:
            es_resaltado = (p["id"] == self.base_resaltada_id)
            card = ctk.CTkFrame(
                self.scroll,
                fg_color="#2b2b2b",
                corner_radius=8,
                border_width=2 if es_resaltado else 0,
                border_color="#db4e17" if es_resaltado else "#2b2b2b"
            )
            card.pack(fill="x", pady=5, padx=8)
            card.grid_columnconfigure(0, weight=1)

            f_info = nuevo_frame(card, color_fondo="transparent")
            f_info.grid(row=0, column=0, sticky="w", padx=12, pady=10)

            titulo = p["nombre"]
            if es_resaltado:
                titulo += "   ⚠️ [PRODUCTO BASE REQUERIDO]"

            nuevo_label(
                f_info,
                titulo,
                fuente=("Arial", 12, "bold"),
                color_texto="#db4e17" if es_resaltado else "#ffffff",
                poscicion="w"
            ).pack(anchor="w")

            nuevo_label(
                f_info,
                f"Stock actual: {p['stock']} uds  |  Tipo: {'Paquete' if p['es_paquete'] else 'Unitario'}",
                fuente=("Arial", 11),
                color_texto="#a0a0a0",
                poscicion="w"
            ).pack(anchor="w", pady=(2, 0))

            nuevo_boton(
                card,
                "Reactivar",
                comando=lambda pid=p["id"]: self.reactivar(pid),
                color_fondo=COLOR_EXITO,
                color_hover=COLOR_EXITO_HOVER,
                ancho=110
            ).grid(row=0, column=1, padx=12, pady=10)

    def reactivar(self, prod_id):
        exito, _ = reactivar_producto_db(prod_id)
        if exito:
            self.renderizar()
            self.callback_actualizar()