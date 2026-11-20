import tkinter.messagebox as messagebox
import customtkinter as ctk
from ui.componentes.configuracion_componentes import ConfiguracionComponentes
from ui.componentes.creador_componentes import *
from bll.gestor_notificaciones import (
    obtener_notificaciones,
    ignorar_notificacion,
    ETIQUETAS_TIPO
)
from bll.gestor_caja import cerrar_caja_definitiva
from ui.modales.modal_notificaciones import (
    ModalNotificacionesIgnoradas,
    ModalAccionStock,
    ModalAccionCosto,
    ModalProductosInactivosNotif
)
from ui.modales.modal_cierre_caja import ModalCierreCaja


class VistaNotificaciones(ConfiguracionComponentes):
    def __init__(self, master):
        super().__init__(master)

        # --- CABECERA SUPERIOR ---
        frame_top = nuevo_frame(self, color_fondo="transparent")
        frame_top.pack(fill="x", padx=20, pady=15)

        nuevo_label(frame_top, "Centro de Notificaciones", fuente=FUENTE_TITULOS).pack(side="left")

        self.btn_ignoradas = nuevo_boton(
            frame_top,
            "Notificaciones Ignoradas",
            comando=self.abrir_ignoradas,
            color_fondo="#555555",
            color_hover="#777777",
            ancho=220
        )
        self.btn_ignoradas.pack(side="right")

        # --- BARRA DE FILTROS (TIPO Y PRIORIDAD) ---
        frame_filtros = nuevo_frame(self, color_fondo="#202020", radio_esquinas=8)
        frame_filtros.pack(fill="x", padx=20, pady=(0, 10))

        nuevo_label(frame_filtros, "Tipo:", fuente=("Arial", 12, "bold"), color_texto="#a0a0a0").pack(side="left", padx=(15, 8), pady=10)

        self.mapa_filtros = {"Todos": "Todos"}
        for codigo, etiqueta in ETIQUETAS_TIPO.items():
            self.mapa_filtros[etiqueta] = codigo

        self.combo_filtro = ctk.CTkComboBox(
            frame_filtros,
            values=list(self.mapa_filtros.keys()),
            command=lambda _: self.cargar_notificaciones(),
            width=220,
            font=("Arial", 12, "bold")
        )
        self.combo_filtro.set("Todos")
        self.combo_filtro.pack(side="left", pady=10)

        nuevo_label(frame_filtros, "Prioridad:", fuente=("Arial", 12, "bold"), color_texto="#a0a0a0").pack(side="left", padx=(20, 8), pady=10)

        self.combo_prioridad = ctk.CTkComboBox(
            frame_filtros,
            values=["Todas", "Alta", "Media", "Baja"],
            command=lambda _: self.cargar_notificaciones(),
            width=140,
            font=("Arial", 12, "bold")
        )
        self.combo_prioridad.set("Todas")
        self.combo_prioridad.pack(side="left", pady=10)

        self.lbl_contador_vista = nuevo_label(frame_filtros, "", fuente=("Arial", 12, "bold"), color_texto="#4fa6ff")
        self.lbl_contador_vista.pack(side="right", padx=15)

        # --- LISTA PRINCIPAL ---
        self.scroll_notifs = ctk.CTkScrollableFrame(self, fg_color="#202020", corner_radius=10)
        self.scroll_notifs.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        self.cargar_notificaciones()

    def abrir_ignoradas(self):
        ModalNotificacionesIgnoradas(self.winfo_toplevel(), self.cargar_notificaciones)

    def cargar_notificaciones(self):
        for w in self.scroll_notifs.winfo_children():
            w.destroy()

        etiqueta_sel = self.combo_filtro.get()
        codigo_tipo = self.mapa_filtros.get(etiqueta_sel, "Todos")
        prioridad_sel = self.combo_prioridad.get()

        activas = obtener_notificaciones(
            estado="Activa",
            filtro_tipo=codigo_tipo,
            filtro_prioridad=prioridad_sel
        )
        ignoradas_total = len(obtener_notificaciones(estado="Ignorada"))

        self.btn_ignoradas.configure(text=f"Notificaciones Ignoradas ({ignoradas_total})")
        self.lbl_contador_vista.configure(text=f"{len(activas)} pendiente(s)")

        ventana_ppal = self.winfo_toplevel()
        if hasattr(ventana_ppal, "actualizar_contador_notificaciones"):
            ventana_ppal.actualizar_contador_notificaciones()

        if not activas:
            nuevo_label(
                self.scroll_notifs,
                "¡Todo en orden! No hay notificaciones pendientes con este filtro.",
                fuente=("Arial", 15, "bold"),
                color_texto=COLOR_EXITO
            ).pack(expand=True, pady=80)
            return

        for n in activas:
            self.crear_tarjeta_notificacion(n)

    def crear_tarjeta_notificacion(self, notif):
        es_alta = notif["prioridad"] == "Alta"
        color_borde = COLOR_FALLO if es_alta else "#d4ac0d"
        texto_prio = "ALTA PRIORIDAD" if es_alta else "ATENCIÓN"

        card = ctk.CTkFrame(
            self.scroll_notifs,
            fg_color="#2b2b2b",
            corner_radius=10,
            border_width=2,
            border_color=color_borde
        )
        card.pack(fill="x", pady=6, padx=10)
        card.grid_columnconfigure(0, weight=1)

        f_izq = nuevo_frame(card, color_fondo="transparent")
        f_izq.grid(row=0, column=0, sticky="w", padx=15, pady=12)

        f_meta = nuevo_frame(f_izq, color_fondo="transparent")
        f_meta.pack(anchor="w")

        nuevo_label(
            f_meta,
            f"● {texto_prio}  |  {notif['etiqueta_tipo']}",
            fuente=("Arial", 12, "bold"),
            color_texto=color_borde,
            poscicion="w"
        ).pack(side="left")

        nuevo_label(
            f_meta,
            f"   ({notif['fecha']})",
            fuente=("Arial", 11),
            color_texto="#a0a0a0",
            poscicion="w"
        ).pack(side="left")

        lbl_desc = nuevo_label(f_izq, notif["descripcion"], fuente=("Arial", 13, "bold"), color_texto="#ffffff", poscicion="w")
        lbl_desc.configure(wraplength=630, justify="left")
        lbl_desc.pack(anchor="w", pady=(6, 0))

        f_der = nuevo_frame(card, color_fondo="transparent")
        f_der.grid(row=0, column=1, sticky="e", padx=15, pady=12)

        texto_accion, color_accion, hover_accion = self.obtener_config_accion(notif["tipo"])

        nuevo_boton(
            f_der,
            texto_accion,
            comando=lambda item=notif: self.ejecutar_accion(item),
            color_fondo=color_accion,
            color_hover=hover_accion,
            ancho=140
        ).grid(row=0, column=0, padx=(0, 8))

        nuevo_boton(
            f_der,
            "Ignorar",
            comando=lambda nid=notif["id"]: self.ignorar_item(nid),
            color_fondo="#444444",
            color_hover="#666666",
            ancho=95
        ).grid(row=0, column=1)

    def obtener_config_accion(self, tipo):
        if tipo in ("STOCK_NEGATIVO", "STOCK_AGOTADO"):
            return "Añadir Stock", COLOR_EXITO, COLOR_EXITO_HOVER
        if tipo == "COSTO_CERO":
            return "Editar Costo", "#1f538d", "#14375e"
        if tipo == "BASE_INACTIVA":
            return "Ver Inactivos", "#db4e17", "#922F10"
        if tipo == "CAJA_INCOMPLETA":
            return "Auditar", "#db4e17", "#922F10"
        if tipo == "VENTA_ANTIGUA":
            return "Ver Guardadas", "#d4ac0d", "#b9770e"
        return "Revisar", "#1f538d", "#14375e"

    def ejecutar_accion(self, notif):
        ventana_ppal = self.winfo_toplevel()
        usuario_actual = getattr(ventana_ppal, "usuario_actual", {}) or {}
        es_admin = usuario_actual.get("rol") == "Administrador"
        nombre_usuario = usuario_actual.get("nombre", "Usuario")
        tipo = notif["tipo"]
        entidad_id = notif.get("entidad_id")

        if tipo in ("STOCK_NEGATIVO", "STOCK_AGOTADO"):
            ModalAccionStock(ventana_ppal, entidad_id, self.cargar_notificaciones)

        elif tipo == "COSTO_CERO":
            if not es_admin:
                messagebox.showwarning("Acceso Denegado", "Solo el Administrador puede editar el costo de un producto.")
                return
            ModalAccionCosto(ventana_ppal, entidad_id, es_admin, self.cargar_notificaciones)

        elif tipo == "BASE_INACTIVA":
            ModalProductosInactivosNotif(ventana_ppal, entidad_id, self.cargar_notificaciones)

        elif tipo == "CAJA_INCOMPLETA":
            def confirmar_auditoria(efectivo_fisico, diferencia):
                exito, _ = cerrar_caja_definitiva(entidad_id, efectivo_fisico, diferencia, auditada_por=nombre_usuario)
                if exito:
                    self.cargar_notificaciones()

            ModalCierreCaja(ventana_ppal, entidad_id, confirmar_auditoria)

        elif tipo == "VENTA_ANTIGUA":
            from bll.gestor_caja import obtener_caja_por_venta
            caja_origen = obtener_caja_por_venta(entidad_id)
            if not caja_origen:
                messagebox.showwarning("Aviso", "No se encontró el turno asociado a esta venta guardada.")
                return

            ventana_ppal.mostrar_historial()
            if hasattr(ventana_ppal.vista_actual, "abrir_guardadas_de_turno"):
                ventana_ppal.after(100, lambda: ventana_ppal.vista_actual.abrir_guardadas_de_turno(caja_origen, venta_resaltada_id=entidad_id))

    def ignorar_item(self, notif_id):
        usuario = getattr(self.winfo_toplevel(), "usuario_actual", {}).get("nombre", "Usuario")
        if ignorar_notificacion(notif_id, usuario):
            self.cargar_notificaciones()