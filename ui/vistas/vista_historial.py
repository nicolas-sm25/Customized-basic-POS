import customtkinter as ctk
from bll.gestor_caja import obtener_historial_cajas
from ui.componentes.configuracion_componentes import ConfiguracionComponentes
from ui.componentes.creador_componentes import *

class VistaHistorial(ConfiguracionComponentes):
    def __init__(self, master):
        super().__init__(master)
        
        self.lbl_titulo = nuevo_label(self, "Historial de Cajas y Rendimiento", fuente=FUENTE_TITULOS)
        self.lbl_titulo.pack(pady=15)

        self.frame_tabla_container = nuevo_frame(self, color_fondo="#202020", radio_esquinas=10)
        self.frame_tabla_container.pack(fill="both", expand=True, padx=20, pady=10)

        self.scroll_tabla = ctk.CTkScrollableFrame(self.frame_tabla_container, fg_color="transparent")
        self.scroll_tabla.pack(fill="both", expand=True, padx=10, pady=10)

        self.cargar_historial()

    def cargar_historial(self):
        for widget in self.scroll_tabla.winfo_children():
            widget.destroy()

        historial = obtener_historial_cajas()

        if not historial:
            nuevo_label(self.scroll_tabla, "No hay historial de cajas registrado.", fuente=("Arial", 16, "bold"), color_texto="#a0a0a0").pack(expand=True, pady=40)
            return

        # --- CABECERA DE LA TABLA ---
        f_enc = nuevo_frame(self.scroll_tabla, color_fondo="#1a1a1a")
        f_enc.pack(fill="x", pady=(0, 5), padx=5)
        
        cols = [1, 2, 2, 2, 2, 2, 2, 2] 
        for i, weight in enumerate(cols):
            f_enc.grid_columnconfigure(i, weight=weight, uniform="hist")
            
        # Reemplazamos "Estado" por "Efect. Físico"
        titulos = [("ID", "center"), ("Fecha", "center"), ("Base", "e"), ("Ventas", "e"), ("Gastos", "e"), ("Ganancia Neta", "e"), ("Diferencia", "e"), ("Efect. Físico", "e")]
        for idx, (texto, alinear) in enumerate(titulos):
            anclaje = "nsew" if alinear == "center" else alinear
            nuevo_label(f_enc, texto, fuente=("Arial", 13, "bold"), color_texto="#a0a0a0", poscicion=alinear).grid(row=0, column=idx, sticky=anclaje, padx=5, pady=8)

        # --- FILAS DE DATOS ---
        for caja in historial:
            f_item = nuevo_frame(self.scroll_tabla, color_fondo="#2b2b2b")
            f_item.pack(fill="x", pady=4, padx=5)
            
            for i, weight in enumerate(cols):
                f_item.grid_columnconfigure(i, weight=weight, uniform="hist")

            nuevo_label(f_item, f"#{caja['id']}", fuente=("Arial", 13, "bold"), poscicion="center").grid(row=0, column=0, sticky="nsew", pady=10)
            nuevo_label(f_item, caja['fecha'], fuente=("Arial", 12), poscicion="center").grid(row=0, column=1, sticky="nsew", pady=10)
            nuevo_label(f_item, f"${int(caja['base']):,}".replace(",", "."), fuente=("Arial", 12), poscicion="e").grid(row=0, column=2, sticky="e", pady=10, padx=5)
            nuevo_label(f_item, f"${int(caja['ventas']):,}".replace(",", "."), fuente=("Arial", 12, "bold"), color_texto=COLOR_EXITO, poscicion="e").grid(row=0, column=3, sticky="e", pady=10, padx=5)
            nuevo_label(f_item, f"${int(caja['gastos']):,}".replace(",", "."), fuente=("Arial", 12), color_texto=COLOR_FALLO, poscicion="e").grid(row=0, column=4, sticky="e", pady=10, padx=5)
            nuevo_label(f_item, f"${int(caja['ganancia_neta']):,}".replace(",", "."), fuente=("Arial", 13, "bold"), color_texto="#4fa6ff", poscicion="e").grid(row=0, column=5, sticky="e", pady=10, padx=5)
            
            dif = caja['diferencia']
            col_dif = COLOR_EXITO if dif >= 0 else COLOR_FALLO
            txt_dif = f"+${int(dif):,}".replace(",", ".") if dif >= 0 else f"-${abs(int(dif)):,}".replace(",", ".")
            if caja['estado'] == "Abierta":
                txt_dif, col_dif = "-", "#a0a0a0"
                
            nuevo_label(f_item, txt_dif, fuente=("Arial", 13, "bold"), color_texto=col_dif, poscicion="e").grid(row=0, column=6, sticky="e", pady=10, padx=5)
            
            # Mostramos el efectivo físico total contado en caja (si está cerrada, base + efectivo ventas - gastos + diferencia)
            efectivo_fisico_real = (caja['base'] + caja['ventas'] - caja['gastos'] + caja['diferencia']) if caja['estado'] == "Cerrada" else 0
            txt_efectivo = f"${int(efectivo_fisico_real):,}".replace(",", ".") if caja['estado'] == "Cerrada" else "En curso..."
            
            nuevo_label(f_item, txt_efectivo, fuente=("Arial", 12, "bold"), color_texto="#ffffff" if caja['estado'] == "Cerrada" else "#d4ac0d", poscicion="e").grid(row=0, column=7, sticky="e", pady=10, padx=5)