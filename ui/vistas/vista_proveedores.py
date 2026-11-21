import tkinter.messagebox as messagebox
import customtkinter as ctk
from ui.componentes.configuracion_componentes import ConfiguracionComponentes
from ui.componentes.creador_componentes import *
from bll.gestor_proveedores import (
    obtener_proveedores,
    obtener_proveedor_por_id,
    obtener_productos_para_proveedor,
    agregar_proveedor,
    actualizar_proveedor,
    eliminar_proveedor
)


class ModalProductosProveedor:
    """Muestra la lista completa de productos vinculados a un proveedor."""
    def __init__(self, master, proveedor_dict):
        self.modal = nuevo_modal(master, f"Productos de {proveedor_dict['proveedor']}", 520, 440)
        self.modal.focus_force()

        frame = nuevo_frame(self.modal)
        frame.pack(expand=True, fill="both", padx=20, pady=15)

        nuevo_label(
            frame,
            f"{proveedor_dict['proveedor']} ({proveedor_dict['cantidad_productos']} productos)",
            fuente=("Arial", 16, "bold"),
            color_texto="#4fa6ff"
        ).pack(pady=(0, 4))

        nuevo_label(
            frame,
            f"Contacto: {proveedor_dict['nombre_proveedor']}  |  Tel: {proveedor_dict['telefono']}",
            fuente=("Arial", 12),
            color_texto="#a0a0a0"
        ).pack(pady=(0, 10))

        scroll = ctk.CTkScrollableFrame(frame, fg_color="#202020")
        scroll.pack(fill="both", expand=True, pady=5)

        productos = proveedor_dict.get("productos", [])
        if not productos:
            nuevo_label(
                scroll,
                "Este proveedor aún no tiene productos asociados.",
                fuente=("Arial", 13),
                color_texto="#a0a0a0"
            ).pack(pady=40)
        else:
            for idx, nombre_prod in enumerate(productos, start=1):
                fila = nuevo_frame(scroll, color_fondo="#2b2b2b")
                fila.pack(fill="x", pady=3, padx=6)
                nuevo_label(
                    fila,
                    f"{idx}.  {nombre_prod}",
                    fuente=("Arial", 12, "bold"),
                    color_texto="#ffffff",
                    poscicion="w"
                ).pack(anchor="w", padx=12, pady=7)

        nuevo_boton(
            frame,
            "Cerrar (Esc)",
            comando=self.modal.destroy,
            color_fondo=COLOR_FALLO,
            color_hover=COLOR_FALLO_HOVER,
            ancho=140
        ).pack(pady=(10, 0))
        self.modal.bind("<Escape>", lambda e: self.modal.destroy())


class ModalAgregarProveedor:
    """Modal para crear un nuevo proveedor y asociarle productos."""
    def __init__(self, master, callback_actualizar):
        self.callback_actualizar = callback_actualizar
        self.modal = nuevo_modal(master, "Agregar Nuevo Proveedor", 620, 620)
        self.modal.focus_force()

        frame_ppal = nuevo_frame(self.modal)
        frame_ppal.pack(expand=True, fill="both", padx=25, pady=15)

        nuevo_label(frame_ppal, "Nuevo Proveedor", fuente=FUENTE_TITULOS).pack(pady=(0, 12))

        f_form = nuevo_frame(frame_ppal, color_fondo="#202020", radio_esquinas=8)
        f_form.pack(fill="x", pady=(0, 10))
        f_form.grid_columnconfigure(0, weight=1)
        f_form.grid_columnconfigure(1, weight=1)

        f_c1 = nuevo_frame(f_form, color_fondo="transparent")
        f_c1.grid(row=0, column=0, sticky="ew", padx=12, pady=(10, 5))
        nuevo_label(f_c1, "Proveedor (Empresa / Marca) *:", fuente=("Arial", 12, "bold"), poscicion="w").pack(anchor="w")
        self.entry_proveedor = nueva_caja_texto(f_c1, placeholder="Ej: Alpina S.A.")
        self.entry_proveedor.pack(fill="x", pady=(3, 0))

        f_c2 = nuevo_frame(f_form, color_fondo="transparent")
        f_c2.grid(row=0, column=1, sticky="ew", padx=12, pady=(10, 5))
        nuevo_label(f_c2, "Nombre Proveedor (Asesor) *:", fuente=("Arial", 12, "bold"), poscicion="w").pack(anchor="w")
        self.entry_nombre = nueva_caja_texto(f_c2, placeholder="Ej: Carlos Gómez")
        self.entry_nombre.pack(fill="x", pady=(3, 0))

        f_c3 = nuevo_frame(f_form, color_fondo="transparent")
        f_c3.grid(row=1, column=0, sticky="ew", padx=12, pady=(5, 12))
        nuevo_label(f_c3, "Teléfono:", fuente=("Arial", 12, "bold"), poscicion="w").pack(anchor="w")
        self.entry_telefono = nueva_caja_texto(f_c3, placeholder="Ej: 3101234567")
        self.entry_telefono.pack(fill="x", pady=(3, 0))

        f_c4 = nuevo_frame(f_form, color_fondo="transparent")
        f_c4.grid(row=1, column=1, sticky="ew", padx=12, pady=(5, 12))
        nuevo_label(f_c4, "NIT:", fuente=("Arial", 12, "bold"), poscicion="w").pack(anchor="w")
        self.entry_nit = nueva_caja_texto(f_c4, placeholder="Ej: 860025900-2")
        self.entry_nit.pack(fill="x", pady=(3, 0))

        f_prod_header = nuevo_frame(frame_ppal, color_fondo="transparent")
        f_prod_header.pack(fill="x", pady=(4, 4))

        nuevo_label(
            f_prod_header,
            "Productos que suministra (Opcional):",
            fuente=("Arial", 12, "bold"),
            color_texto="#d4ac0d"
        ).pack(side="left")

        self.entry_buscar_prod = nueva_caja_texto(f_prod_header, placeholder="Filtrar producto...", ancho=210)
        self.entry_buscar_prod.pack(side="right")
        self.entry_buscar_prod.bind("<KeyRelease>", lambda e: self.filtrar_productos())

        self.scroll_prods = ctk.CTkScrollableFrame(frame_ppal, fg_color="#202020", height=180)
        self.scroll_prods.pack(fill="both", expand=True, pady=(0, 8))

        self.todos_productos = obtener_productos_para_proveedor()
        self.seleccionados = {p["id"]: ctk.BooleanVar(value=False) for p in self.todos_productos}

        self.filtrar_productos()

        self.lbl_error = nuevo_label(frame_ppal, "", fuente=("Arial", 11, "bold"), color_texto=COLOR_FALLO)
        self.lbl_error.pack(pady=(0, 6))

        f_btns = nuevo_frame(frame_ppal, color_fondo="transparent")
        f_btns.pack()

        nuevo_boton(
            f_btns,
            "Guardar Proveedor",
            comando=self.guardar,
            color_fondo=COLOR_EXITO,
            color_hover=COLOR_EXITO_HOVER,
            ancho=160
        ).pack(side="left", padx=10)

        nuevo_boton(
            f_btns,
            "Cancelar (Esc)",
            comando=self.modal.destroy,
            color_fondo="#555555",
            color_hover="#777777",
            ancho=140
        ).pack(side="left", padx=10)

        self.modal.bind("<Escape>", lambda e: self.modal.destroy())
        self.modal.after(50, self.entry_proveedor.focus)

    def filtrar_productos(self):
        for w in self.scroll_prods.winfo_children():
            w.destroy()

        criterio = self.entry_buscar_prod.get().strip().lower()
        filtrados = [
            p for p in self.todos_productos
            if not criterio or criterio in p["nombre"].lower()
        ]

        if not filtrados:
            nuevo_label(self.scroll_prods, "No hay productos que coincidan.", color_texto="#a0a0a0").pack(pady=20)
            return

        for p in filtrados:
            texto_cb = p["nombre"]
            if p["proveedor_actual"]:
                texto_cb += f"  (Actual: {p['proveedor_actual']})"

            cb = ctk.CTkCheckBox(
                self.scroll_prods,
                text=texto_cb,
                variable=self.seleccionados[p["id"]],
                font=("Arial", 12),
                text_color="#ffffff" if not p["proveedor_actual"] else "#cccccc"
            )
            cb.pack(anchor="w", padx=10, pady=4)

    def guardar(self):
        ids_elegidos = [pid for pid, var in self.seleccionados.items() if var.get()]
        exito, msg = agregar_proveedor(
            proveedor=self.entry_proveedor.get(),
            nombre_proveedor=self.entry_nombre.get(),
            telefono=self.entry_telefono.get(),
            nit=self.entry_nit.get(),
            ids_productos=ids_elegidos
        )

        if exito:
            self.modal.destroy()
            self.callback_actualizar()
        else:
            self.lbl_error.configure(text=msg)


class ModalEditarProveedor:
    """Modal para editar datos/productos de un proveedor o eliminarlo limpiamente."""
    def __init__(self, master, proveedor_id, callback_actualizar):
        self.proveedor_id = proveedor_id
        self.callback_actualizar = callback_actualizar
        self.datos_prov = obtener_proveedor_por_id(proveedor_id)

        self.modal = nuevo_modal(master, "Editar Proveedor", 640, 640)
        self.modal.focus_force()

        frame_ppal = nuevo_frame(self.modal)
        frame_ppal.pack(expand=True, fill="both", padx=25, pady=15)

        if not self.datos_prov:
            nuevo_label(frame_ppal, "No se encontró el proveedor.", color_texto=COLOR_FALLO).pack(pady=40)
            nuevo_boton(frame_ppal, "Cerrar", comando=self.modal.destroy, color_fondo=COLOR_FALLO).pack()
            return

        nuevo_label(frame_ppal, f"Editar: {self.datos_prov['proveedor']}", fuente=FUENTE_TITULOS).pack(pady=(0, 12))

        f_form = nuevo_frame(frame_ppal, color_fondo="#202020", radio_esquinas=8)
        f_form.pack(fill="x", pady=(0, 10))
        f_form.grid_columnconfigure(0, weight=1)
        f_form.grid_columnconfigure(1, weight=1)

        f_c1 = nuevo_frame(f_form, color_fondo="transparent")
        f_c1.grid(row=0, column=0, sticky="ew", padx=12, pady=(10, 5))
        nuevo_label(f_c1, "Proveedor (Empresa / Marca) *:", fuente=("Arial", 12, "bold"), poscicion="w").pack(anchor="w")
        self.entry_proveedor = nueva_caja_texto(f_c1, placeholder="Ej: Alpina S.A.")
        self.entry_proveedor.insert(0, self.datos_prov["proveedor"])
        self.entry_proveedor.pack(fill="x", pady=(3, 0))

        f_c2 = nuevo_frame(f_form, color_fondo="transparent")
        f_c2.grid(row=0, column=1, sticky="ew", padx=12, pady=(10, 5))
        nuevo_label(f_c2, "Nombre Proveedor (Asesor) *:", fuente=("Arial", 12, "bold"), poscicion="w").pack(anchor="w")
        self.entry_nombre = nueva_caja_texto(f_c2, placeholder="Ej: Carlos Gómez")
        self.entry_nombre.insert(0, self.datos_prov["nombre_proveedor"])
        self.entry_nombre.pack(fill="x", pady=(3, 0))

        f_c3 = nuevo_frame(f_form, color_fondo="transparent")
        f_c3.grid(row=1, column=0, sticky="ew", padx=12, pady=(5, 12))
        nuevo_label(f_c3, "Teléfono:", fuente=("Arial", 12, "bold"), poscicion="w").pack(anchor="w")
        self.entry_telefono = nueva_caja_texto(f_c3, placeholder="Ej: 3101234567")
        if self.datos_prov["telefono"]:
            self.entry_telefono.insert(0, self.datos_prov["telefono"])
        self.entry_telefono.pack(fill="x", pady=(3, 0))

        f_c4 = nuevo_frame(f_form, color_fondo="transparent")
        f_c4.grid(row=1, column=1, sticky="ew", padx=12, pady=(5, 12))
        nuevo_label(f_c4, "NIT:", fuente=("Arial", 12, "bold"), poscicion="w").pack(anchor="w")
        self.entry_nit = nueva_caja_texto(f_c4, placeholder="Ej: 860025900-2")
        if self.datos_prov["nit"]:
            self.entry_nit.insert(0, self.datos_prov["nit"])
        self.entry_nit.pack(fill="x", pady=(3, 0))

        f_prod_header = nuevo_frame(frame_ppal, color_fondo="transparent")
        f_prod_header.pack(fill="x", pady=(4, 4))

        nuevo_label(
            f_prod_header,
            "Productos suministrados:",
            fuente=("Arial", 12, "bold"),
            color_texto="#d4ac0d"
        ).pack(side="left")

        self.entry_buscar_prod = nueva_caja_texto(f_prod_header, placeholder="Filtrar producto...", ancho=210)
        self.entry_buscar_prod.pack(side="right")
        self.entry_buscar_prod.bind("<KeyRelease>", lambda e: self.filtrar_productos())

        self.scroll_prods = ctk.CTkScrollableFrame(frame_ppal, fg_color="#202020", height=180)
        self.scroll_prods.pack(fill="both", expand=True, pady=(0, 8))

        ids_asignados = set(self.datos_prov["ids_productos"])
        todos = obtener_productos_para_proveedor()
        todos.sort(key=lambda p: (0 if p["id"] in ids_asignados else 1, p["nombre"].lower()))

        self.todos_productos = todos
        self.seleccionados = {
            p["id"]: ctk.BooleanVar(value=(p["id"] in ids_asignados))
            for p in self.todos_productos
        }

        self.filtrar_productos()

        self.lbl_error = nuevo_label(frame_ppal, "", fuente=("Arial", 11, "bold"), color_texto=COLOR_FALLO)
        self.lbl_error.pack(pady=(0, 8))

        f_btns = nuevo_frame(frame_ppal, color_fondo="transparent")
        f_btns.pack(fill="x")

        nuevo_boton(
            f_btns,
            "Eliminar",
            comando=self.confirmar_eliminacion,
            color_fondo=COLOR_FALLO,
            color_hover=COLOR_FALLO_HOVER,
            ancho=120
        ).pack(side="left")

        nuevo_boton(
            f_btns,
            "Cancelar (Esc)",
            comando=self.modal.destroy,
            color_fondo="#555555",
            color_hover="#777777",
            ancho=130
        ).pack(side="right", padx=(8, 0))

        nuevo_boton(
            f_btns,
            "Guardar Cambios",
            comando=self.guardar_cambios,
            color_fondo=COLOR_EXITO,
            color_hover=COLOR_EXITO_HOVER,
            ancho=150
        ).pack(side="right")

        self.modal.bind("<Escape>", lambda e: self.modal.destroy())
        self.modal.after(50, self.entry_proveedor.focus)

    def filtrar_productos(self):
        for w in self.scroll_prods.winfo_children():
            w.destroy()

        criterio = self.entry_buscar_prod.get().strip().lower()
        filtrados = [
            p for p in self.todos_productos
            if not criterio or criterio in p["nombre"].lower()
        ]

        if not filtrados:
            nuevo_label(self.scroll_prods, "No hay productos que coincidan.", color_texto="#a0a0a0").pack(pady=20)
            return

        for p in filtrados:
            texto_cb = p["nombre"]
            if p["proveedor_actual"] and p["proveedor_id"] != self.proveedor_id:
                texto_cb += f"  (Actual: {p['proveedor_actual']})"

            cb = ctk.CTkCheckBox(
                self.scroll_prods,
                text=texto_cb,
                variable=self.seleccionados[p["id"]],
                font=("Arial", 12),
                text_color="#ffffff"
            )
            cb.pack(anchor="w", padx=10, pady=4)

    def guardar_cambios(self):
        ids_elegidos = [pid for pid, var in self.seleccionados.items() if var.get()]
        exito, msg = actualizar_proveedor(
            proveedor_id=self.proveedor_id,
            proveedor=self.entry_proveedor.get(),
            nombre_proveedor=self.entry_nombre.get(),
            telefono=self.entry_telefono.get(),
            nit=self.entry_nit.get(),
            ids_productos=ids_elegidos
        )

        if exito:
            self.modal.destroy()
            self.callback_actualizar()
        else:
            self.lbl_error.configure(text=msg)

    def confirmar_eliminacion(self):
        confirmar = messagebox.askyesno(
            "Eliminar Proveedor",
            f"¿Seguro que deseas eliminar al proveedor '{self.datos_prov['proveedor']}'?\n\n"
            "Sus productos NO se borrarán del inventario, simplemente quedarán sin proveedor asignado.",
            parent=self.modal
        )
        if not confirmar:
            return

        exito, msg = eliminar_proveedor(self.proveedor_id)
        if exito:
            self.modal.destroy()
            self.callback_actualizar()
        else:
            self.lbl_error.configure(text=msg)


class VistaProveedores(ConfiguracionComponentes):
    def __init__(self, master):
        super().__init__(master)

        # --- CABECERA ---
        frame_top = nuevo_frame(self, color_fondo="transparent")
        frame_top.pack(fill="x", padx=20, pady=15)

        nuevo_label(frame_top, "Gestión de Proveedores", fuente=FUENTE_TITULOS).pack(side="left")

        nuevo_boton(
            frame_top,
            "+ Agregar Proveedor",
            comando=self.abrir_modal_agregar,
            color_fondo=COLOR_EXITO,
            color_hover=COLOR_EXITO_HOVER,
            ancho=180
        ).pack(side="right")

        # --- CONTENEDOR TABLA + PAGINACIÓN ---
        self.frame_contenedor = nuevo_frame(self, color_fondo="#202020", radio_esquinas=10)
        self.frame_contenedor.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        self.frame_lista = nuevo_frame(self.frame_contenedor, color_fondo="transparent")
        self.frame_lista.pack(fill="both", expand=True, padx=10, pady=10)

        self.pagina_actual = 1
        self.items_por_pagina = 8
        self.proveedores = []

        self.frame_paginacion = nuevo_frame(self.frame_contenedor, color_fondo="transparent")
        self.frame_paginacion.pack(fill="x", pady=(0, 10))

        self.btn_menos_5 = nuevo_boton(self.frame_paginacion, "<< 5 Pags", comando=lambda: self.cambiar_pagina(-5), ancho=90, color_fondo="#1f538d")
        self.btn_menos_5.pack(side="left", padx=(20, 5))

        self.btn_menos_1 = nuevo_boton(self.frame_paginacion, "< Anterior", comando=lambda: self.cambiar_pagina(-1), ancho=90, color_fondo="#1f538d")
        self.btn_menos_1.pack(side="left", padx=5)

        self.lbl_paginacion = nuevo_label(self.frame_paginacion, "Página 1 / 1", fuente=("Arial", 12, "bold"), color_texto="#a0a0a0")
        self.lbl_paginacion.pack(side="left", expand=True)

        self.btn_mas_5 = nuevo_boton(self.frame_paginacion, "5 Pags >>", comando=lambda: self.cambiar_pagina(5), ancho=90, color_fondo="#1f538d")
        self.btn_mas_5.pack(side="right", padx=(5, 20))

        self.btn_mas_1 = nuevo_boton(self.frame_paginacion, "Siguiente >", comando=lambda: self.cambiar_pagina(1), ancho=90, color_fondo="#1f538d")
        self.btn_mas_1.pack(side="right", padx=5)

        self.cargar_proveedores()

    def abrir_modal_agregar(self):
        ModalAgregarProveedor(self.winfo_toplevel(), self.cargar_proveedores)

    def abrir_modal_editar(self, proveedor_id):
        ModalEditarProveedor(self.winfo_toplevel(), proveedor_id, self.cargar_proveedores)

    def cargar_proveedores(self):
        self.proveedores = obtener_proveedores()
        self.renderizar_pagina()

    def cambiar_pagina(self, salto):
        nueva = self.pagina_actual + salto
        if nueva < 1:
            nueva = 1
        elif nueva > getattr(self, 'total_paginas', 1):
            nueva = getattr(self, 'total_paginas', 1)

        if nueva != self.pagina_actual:
            self.pagina_actual = nueva
            self.renderizar_pagina()

    def renderizar_pagina(self):
        for w in self.frame_lista.winfo_children():
            w.destroy()

        if not self.proveedores:
            nuevo_label(
                self.frame_lista,
                "No hay proveedores registrados. Usa '+ Agregar Proveedor' para crear el primero.",
                fuente=("Arial", 14, "bold"),
                color_texto="#a0a0a0"
            ).pack(expand=True, pady=80)
            self.frame_paginacion.pack_forget()
            return

        self.frame_paginacion.pack(fill="x", pady=(0, 10))
        self.total_paginas = max(1, (len(self.proveedores) + self.items_por_pagina - 1) // self.items_por_pagina)
        if self.pagina_actual > self.total_paginas:
            self.pagina_actual = self.total_paginas

        inicio = (self.pagina_actual - 1) * self.items_por_pagina
        pagina_items = self.proveedores[inicio:inicio + self.items_por_pagina]

        self.lbl_paginacion.configure(text=f"Página {self.pagina_actual} / {self.total_paginas}")
        self.btn_menos_1.configure(state="normal" if self.pagina_actual > 1 else "disabled")
        self.btn_menos_5.configure(state="normal" if self.pagina_actual > 1 else "disabled")
        self.btn_mas_1.configure(state="normal" if self.pagina_actual < self.total_paginas else "disabled")
        self.btn_mas_5.configure(state="normal" if self.pagina_actual < self.total_paginas else "disabled")

        # Cabecera: Proveedor | Nombre Proveedor | Teléfono | NIT | Productos | Acciones
        f_enc = nuevo_frame(self.frame_lista, color_fondo="#1a1a1a")
        f_enc.pack(fill="x", pady=(0, 5), padx=5)
        cols = [3, 3, 2, 2, 2, 2]
        for i, w in enumerate(cols):
            f_enc.grid_columnconfigure(i, weight=w, uniform="tabla_prov")

        titulos = [
            ("Proveedor", "w"),
            ("Nombre Proveedor", "w"),
            ("Teléfono", "center"),
            ("NIT", "center"),
            ("Productos", "center"),
            ("Acciones", "center")
        ]
        for idx, (texto, pos) in enumerate(titulos):
            nuevo_label(f_enc, texto, fuente=("Arial", 12, "bold"), color_texto="#a0a0a0", poscicion=pos).grid(
                row=0, column=idx, sticky="nsew" if pos == "center" else pos, padx=10, pady=8
            )

        for prov in pagina_items:
            f = nuevo_frame(self.frame_lista, color_fondo="#2b2b2b")
            f.pack(fill="x", pady=3, padx=5)
            for i, w in enumerate(cols):
                f.grid_columnconfigure(i, weight=w, uniform="tabla_prov")

            nuevo_label(f, prov["proveedor"], fuente=("Arial", 12, "bold"), color_texto="#4fa6ff", poscicion="w").grid(
                row=0, column=0, sticky="w", padx=10, pady=9
            )
            nuevo_label(f, prov["nombre_proveedor"], fuente=("Arial", 12), color_texto="#ffffff", poscicion="w").grid(
                row=0, column=1, sticky="w", padx=10, pady=9
            )
            nuevo_label(f, prov["telefono"], fuente=("Arial", 12), color_texto="#cccccc", poscicion="center").grid(
                row=0, column=2, sticky="nsew", pady=9
            )
            nuevo_label(f, prov["nit"], fuente=("Arial", 12), color_texto="#d4ac0d", poscicion="center").grid(
                row=0, column=3, sticky="nsew", pady=9
            )

            f_prod = nuevo_frame(f, color_fondo="transparent")
            f_prod.grid(row=0, column=4, sticky="nsew", pady=5)

            cant = prov["cantidad_productos"]
            txt_btn = f"Ver ({cant})" if cant > 0 else "Sin productos"
            nuevo_boton(
                f_prod,
                txt_btn,
                comando=lambda item=prov: ModalProductosProveedor(self.winfo_toplevel(), item),
                color_fondo="#1f538d" if cant > 0 else "#444444",
                color_hover="#14375e" if cant > 0 else "#555555",
                ancho=110
            ).pack(expand=True)

            f_acc = nuevo_frame(f, color_fondo="transparent")
            f_acc.grid(row=0, column=5, sticky="nsew", pady=5)

            nuevo_boton(
                f_acc,
                "Editar",
                comando=lambda pid=prov["id"]: self.abrir_modal_editar(pid),
                color_fondo="#d4ac0d",
                color_hover="#b9770e",
                ancho=95
            ).pack(expand=True)