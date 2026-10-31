import customtkinter as ctk
from ui.componentes.creador_componentes import *
from bll.gestor_caja import obtener_resumen_caja

class ModalCierre:
    def __init__(self, master, caja_id, callback_confirmar):
        self.master = master
        self.modal = nuevo_modal(master, "Resumen y Cierre de Caja", 550, 720)
        self.caja_id = caja_id
        self.callback_confirmar = callback_confirmar

        frame_modal = nuevo_frame(self.modal)
        frame_modal.pack(expand=True, fill="both", padx=20, pady=20)
        
        nuevo_label(frame_modal, "Resumen del Día", fuente=FUENTE_TITULOS).pack(pady=10)
        
        resumen = obtener_resumen_caja(self.caja_id)
        if not resumen:
            nuevo_label(frame_modal, "Error al cargar resumen.", color_texto=COLOR_FALLO).pack()
            return
            
        # --- TABLA DE RENDIMIENTO DESGLOSADA ---
        f_stats = nuevo_frame(frame_modal, color_fondo="#2b2b2b", radio_esquinas=10)
        f_stats.pack(fill="x", pady=10, padx=10)
        
        self.crear_fila_stat(f_stats, "Ventas Efectivo:", f"${int(resumen['efectivo']):,}".replace(",", "."), COLOR_EXITO)
        self.crear_fila_stat(f_stats, "Ventas Nequi:", f"${int(resumen['nequi']):,}".replace(",", "."), "#9d64ff")
        
        nuevo_frame(f_stats, color_fondo="#444444", alto=1).pack(fill="x", padx=30, pady=2)
        
        self.crear_fila_stat(f_stats, "Ganancia Efectivo:", f"${int(resumen['ganancia_efectivo']):,}".replace(",", "."), COLOR_EXITO)
        self.crear_fila_stat(f_stats, "Ganancia Nequi:", f"${int(resumen['ganancia_nequi']):,}".replace(",", "."), "#9d64ff")
        self.crear_fila_stat(f_stats, "Gastos Registrados:", f"- ${int(resumen['gastos']):,}".replace(",", "."), COLOR_FALLO)
        
        nuevo_frame(f_stats, color_fondo="#444444", alto=2).pack(fill="x", padx=15, pady=5)
        self.crear_fila_stat(f_stats, "Ganancia Neta Total:", f"${int(resumen['ganancia_neta']):,}".replace(",", "."), "#4fa6ff", bold=True)
        
        # --- CONTROL DE EFECTIVO FÍSICO ---
        f_flujo = nuevo_frame(frame_modal, color_fondo="#1c1c1c", radio_esquinas=10)
        f_flujo.pack(fill="x", pady=10, padx=10)
        
        nuevo_label(f_flujo, "Cuadre de Caja (Efectivo)", fuente=("Arial", 14, "bold"), color_texto="#d4ac0d").pack(pady=5)
        self.crear_fila_stat(f_flujo, "Base Inicial:", f"${int(resumen['base']):,}".replace(",", "."))
        self.crear_fila_stat(f_flujo, "Entradas (Ventas):", f"+ ${int(resumen['efectivo']):,}".replace(",", "."))
        self.crear_fila_stat(f_flujo, "Salidas (Gastos):", f"- ${int(resumen['gastos']):,}".replace(",", "."))
        
        self.efectivo_esperado = resumen['efectivo_esperado']
        self.crear_fila_stat(f_flujo, "Efectivo Esperado en Caja:", f"${int(self.efectivo_esperado):,}".replace(",", "."), "#d4ac0d", bold=True)
        
        nuevo_label(frame_modal, "Ingrese el efectivo físico contado:", fuente=("Arial", 12, "bold")).pack(pady=(15, 5))
        self.entry_fisico = nueva_caja_texto(frame_modal, placeholder="Monto total contado")
        self.entry_fisico.configure(justify="center", font=("Arial", 20))
        self.entry_fisico.pack(pady=5, ipady=5)
        
        self.lbl_diferencia = nuevo_label(frame_modal, "", fuente=("Arial", 14, "bold"))
        self.lbl_diferencia.pack(pady=5)
        
        frame_botones = nuevo_frame(frame_modal, color_fondo="transparent")
        frame_botones.pack(pady=10)

        nuevo_boton(frame_botones, "Cancelar (Esc)", comando=self.cerrar_modal, color_fondo="#555555", color_hover="#777777").grid(row=0, column=0, padx=10)
        nuevo_boton(frame_botones, "Cerrar Caja (Enter)", comando=self.procesar_cierre, color_fondo=COLOR_FALLO, color_hover=COLOR_FALLO_HOVER).grid(row=0, column=1, padx=10)

        # Atajos
        self.entry_fisico.bind("<KeyRelease>", self.formatear_moneda)
        self.entry_fisico.bind("<Return>", lambda e: self.procesar_cierre())
        self.entry_fisico.bind("<Escape>", lambda e: self.cerrar_modal())
        self.modal.bind("<Escape>", lambda e: self.cerrar_modal())
        self.modal.bind("<Return>", lambda e: self.procesar_cierre())
        
        self.modal.after(50, self.entry_fisico.focus)

    def cerrar_modal(self):
        self.master.focus()
        if hasattr(self.master, 'entry_buscar_prod'):
            self.master.entry_buscar_prod.focus()
        self.modal.destroy()

    def crear_fila_stat(self, master, label, valor, color="#ffffff", bold=False):
        f = nuevo_frame(master, color_fondo="transparent")
        f.pack(fill="x", padx=15, pady=2)
        fuente_val = ("Arial", 14, "bold") if bold else ("Arial", 14)
        nuevo_label(f, label, fuente=("Arial", 13), color_texto="#a0a0a0", poscicion="w").pack(side="left")
        nuevo_label(f, valor, fuente=fuente_val, color_texto=color, poscicion="e").pack(side="right")

    def formatear_moneda(self, event=None):
        texto_limpio = ''.join(filter(str.isdigit, self.entry_fisico.get().replace(".", "")))
        self.entry_fisico.delete(0, 'end')
        
        if texto_limpio:
            self.entry_fisico.insert(0, f"{int(texto_limpio):,}".replace(",", "."))
            diferencia = int(texto_limpio) - self.efectivo_esperado
            if diferencia < 0:
                self.lbl_diferencia.configure(text=f"Faltante: ${int(abs(diferencia)):,}".replace(",", "."), text_color=COLOR_FALLO)
            elif diferencia > 0:
                self.lbl_diferencia.configure(text=f"Sobrante: ${int(diferencia):,}".replace(",", "."), text_color=COLOR_EXITO)
            else:
                self.lbl_diferencia.configure(text="¡Caja Cuadrada Perfectamente!", text_color=COLOR_EXITO)
        else:
            self.lbl_diferencia.configure(text="")

    def procesar_cierre(self):
        texto_limpio = ''.join(filter(str.isdigit, self.entry_fisico.get()))
        if not texto_limpio:
            self.lbl_diferencia.configure(text="Ingrese el valor físico.", text_color=COLOR_FALLO)
            return
            
        efectivo_fisico = int(texto_limpio)
        diferencia = efectivo_fisico - self.efectivo_esperado
        self.modal.destroy()
        self.callback_confirmar(efectivo_fisico, diferencia)