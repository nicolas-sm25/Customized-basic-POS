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
        
        # Ahora son 9 columnas.
        cols = [2, 2, 2, 2, 2, 2, 2, 2, 2] 
        for i, weight in enumerate(cols):
            f_enc.grid_columnconfigure(i, weight=weight, uniform="hist")
            
        titulos = [
            ("Encargado", "w"), 
            ("Apertura", "center"), 
            ("Cierre", "center"),
            ("Base", "e"), 
            ("Ingresos", "e"), 
            ("Gastos", "e"), 
            ("Utilidad", "e"), 
            ("Cuadre", "e"), 
            ("Físico", "e")
        ]
        
        for idx, (texto, alinear) in enumerate(titulos):
            anclaje = "nsew" if alinear == "center" else alinear
            nuevo_label(f_enc, texto, fuente=("Arial", 11, "bold"), color_texto="#a0a0a0", poscicion=alinear).grid(row=0, column=idx, sticky=anclaje, padx=5, pady=8)

        # --- FILAS DE DATOS ---
        for caja in historial:
            f_item = nuevo_frame(self.scroll_tabla, color_fondo="#2b2b2b")
            f_item.pack(fill="x", pady=4, padx=5)
            
            for i, weight in enumerate(cols):
                f_item.grid_columnconfigure(i, weight=weight, uniform="hist")

            # 1. Encargado
            nuevo_label(f_item, caja['encargado'], fuente=("Arial", 11, "bold"), color_texto="#d4ac0d", poscicion="w").grid(row=0, column=0, sticky="w", padx=10, pady=10)
            # 2. Fecha Apertura
            nuevo_label(f_item, caja['fecha_apertura'], fuente=("Arial", 11), poscicion="center").grid(row=0, column=1, sticky="nsew", pady=10)
            
            # 3. Fecha Cierre
            color_cierre = "#d4ac0d" if caja['estado'] == "Abierta" else "#ffffff"
            nuevo_label(f_item, caja['fecha_cierre'], fuente=("Arial", 11, "bold" if caja['estado'] == "Abierta" else "normal"), color_texto=color_cierre, poscicion="center").grid(row=0, column=2, sticky="nsew", pady=10)
            
            # 4. Base
            nuevo_label(f_item, f"${int(caja['base']):,}".replace(",", "."), fuente=("Arial", 11), poscicion="e").grid(row=0, column=3, sticky="e", pady=10, padx=5)
            # 5. Ventas (Ingresos)
            nuevo_label(f_item, f"${int(caja['ventas']):,}".replace(",", "."), fuente=("Arial", 11, "bold"), color_texto=COLOR_EXITO, poscicion="e").grid(row=0, column=4, sticky="e", pady=10, padx=5)
            # 6. Gastos
            nuevo_label(f_item, f"${int(caja['gastos']):,}".replace(",", "."), fuente=("Arial", 11, "bold"), color_texto=COLOR_FALLO, poscicion="e").grid(row=0, column=5, sticky="e", pady=10, padx=5)
            # 7. Ganancia Neta
            nuevo_label(f_item, f"${int(caja['ganancia_neta']):,}".replace(",", "."), fuente=("Arial", 11, "bold"), color_texto="#4fa6ff", poscicion="e").grid(row=0, column=6, sticky="e", pady=10, padx=5)
            
            # 8. Diferencia (Cuadre)
            dif = caja['diferencia']
            col_dif = COLOR_EXITO if dif >= 0 else COLOR_FALLO
            txt_dif = f"+${int(dif):,}".replace(",", ".") if dif >= 0 else f"-${abs(int(dif)):,}".replace(",", ".")
            if caja['estado'] == "Abierta":
                txt_dif, col_dif = "-", "#a0a0a0"
                
            nuevo_label(f_item, txt_dif, fuente=("Arial", 11, "bold"), color_texto=col_dif, poscicion="e").grid(row=0, column=7, sticky="e", pady=10, padx=5)
            
            # 9. Físico
            efectivo_fisico_real = (caja['base'] + caja['ventas'] - caja['gastos'] + caja['diferencia']) if caja['estado'] == "Cerrada" else 0
            txt_efectivo = f"${int(efectivo_fisico_real):,}".replace(",", ".") if caja['estado'] == "Cerrada" else "En curso..."
            
            nuevo_label(f_item, txt_efectivo, fuente=("Arial", 11, "bold"), color_texto="#ffffff" if caja['estado'] == "Cerrada" else "#d4ac0d", poscicion="e").grid(row=0, column=8, sticky="e", pady=10, padx=5)