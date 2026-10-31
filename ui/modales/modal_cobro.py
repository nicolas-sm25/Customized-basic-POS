import customtkinter as ctk
from ui.componentes.creador_componentes import *

class ModalCobro:
    def __init__(self, master, total_actual, callback_procesar):
        self.master = master
        self.modal = nuevo_modal(master, "Cobrar Venta", 500, 450)

        self.callback_procesar = callback_procesar
        self.total_actual = total_actual
        
        texto_limpio = ''.join(filter(str.isdigit, total_actual))
        self.total_num = int(texto_limpio) if texto_limpio else 0

        self.frame_principal = nuevo_frame(self.modal)
        self.frame_principal.pack(expand=True, fill="both", padx=20, pady=20)

        self.mostrar_seleccion_metodo()

    def cerrar_modal(self):
        self.master.focus()
        if hasattr(self.master, 'entry_buscar_prod'):
            self.master.entry_buscar_prod.focus()
        self.modal.destroy()

    # --- SELECCIONAR MÉTODO DE PAGO ---
    def mostrar_seleccion_metodo(self):
        for widget in self.frame_principal.winfo_children():
            widget.destroy()

        nuevo_label(self.frame_principal, "Seleccione Método de Pago", fuente=FUENTE_TITULOS).pack(pady=20)
        nuevo_label(self.frame_principal, f"Total: {self.total_actual}", fuente=("Arial", 32, "bold"), color_texto=COLOR_EXITO).pack(pady=20)

        frame_botones = nuevo_frame(self.frame_principal, color_fondo="transparent")
        frame_botones.pack(pady=20)

        def procesar_nequi():
            self.callback_procesar("Nequi", self, self.total_num, 0)

        nuevo_boton(frame_botones, "Efectivo (Enter)", comando=self.mostrar_ingreso_efectivo, color_fondo=COLOR_EXITO, color_hover=COLOR_EXITO_HOVER, ancho=150).grid(row=0, column=0, padx=10)
        nuevo_boton(frame_botones, "Nequi", comando=procesar_nequi, color_fondo="#5e17eb", color_hover="#4a11c0", ancho=150).grid(row=0, column=1, padx=10)

        nuevo_boton(self.frame_principal, "Regresar (Esc)", comando=self.cerrar_modal, color_fondo=COLOR_FALLO, color_hover=COLOR_FALLO_HOVER).pack(side="bottom", pady=10)

        self.modal.bind("<Escape>", lambda event: self.cerrar_modal())
        self.modal.bind("<Return>", lambda event: self.mostrar_ingreso_efectivo())
        self.modal.bind("<F12>", lambda event: self.mostrar_ingreso_efectivo())

    # --- INGRESO DE EFECTIVO Y VUELTAS ---
    def mostrar_ingreso_efectivo(self):
        for widget in self.frame_principal.winfo_children():
            widget.destroy()

        nuevo_label(self.frame_principal, "Cobro en Efectivo", fuente=FUENTE_TITULOS).pack(pady=(10, 0))
        nuevo_label(self.frame_principal, f"Cobrar: {self.total_actual}", fuente=("Arial", 36, "bold"), color_texto=COLOR_EXITO).pack(pady=(10, 20))

        self.entry_efectivo = nueva_caja_texto(self.frame_principal, placeholder="Efectivo entregado (Enter si es exacto)")
        self.entry_efectivo.configure(font=("Arial", 28), height=50, width=400, justify="center")
        self.entry_efectivo.pack(pady=10)

        self.lbl_cambio = nuevo_label(self.frame_principal, "Cambio: $0", fuente=("Arial", 36, "bold"), color_texto="#d4ac0d")
        self.lbl_cambio.pack(pady=10)

        self.lbl_error = nuevo_label(self.frame_principal, "", color_texto=COLOR_FALLO)
        self.lbl_error.pack(pady=5)

        frame_botones = nuevo_frame(self.frame_principal, color_fondo="transparent")
        frame_botones.pack(pady=10)

        nuevo_boton(frame_botones, "Aceptar (Enter)", comando=self.procesar_efectivo, color_fondo=COLOR_EXITO, color_hover=COLOR_EXITO_HOVER, ancho=150).grid(row=0, column=0, padx=10)
        nuevo_boton(frame_botones, "Regresar (Esc)", comando=self.mostrar_seleccion_metodo, color_fondo=COLOR_FALLO, color_hover=COLOR_FALLO_HOVER, ancho=150).grid(row=0, column=1, padx=10)

        self.entry_efectivo.bind("<KeyRelease>", self.calcular_cambio)
        self.modal.bind("<Return>", lambda event: self.procesar_efectivo())
        self.entry_efectivo.bind("<Return>", lambda event: self.procesar_efectivo())
        self.modal.bind("<Escape>", lambda event: self.mostrar_seleccion_metodo())
        self.entry_efectivo.bind("<Escape>", lambda event: self.mostrar_seleccion_metodo())
        
        self.modal.after(50, self.entry_efectivo.focus)

    # --- CONTROL DE VUELTAS ---
    def calcular_cambio(self, event=None):
        texto_actual = self.entry_efectivo.get().replace(".", "")
        texto_limpio = ''.join(filter(str.isdigit, texto_actual))
        
        self.entry_efectivo.delete(0, 'end')
        
        if texto_limpio:
            texto_formateado = f"{int(texto_limpio):,}".replace(",", ".")
            self.entry_efectivo.insert(0, texto_formateado)
            
            entregado = int(texto_limpio)
            vueltas = entregado - self.total_num
            
            if vueltas >= 0:
                self.lbl_cambio.configure(text=f"Cambio: ${vueltas:,}".replace(",", "."), text_color="#d4ac0d")
                self.lbl_error.configure(text="")
            else:
                self.lbl_cambio.configure(text="¡Falta dinero!", text_color=COLOR_FALLO)
        else:
            self.lbl_cambio.configure(text="Cambio: $0", text_color="#d4ac0d")
            self.lbl_error.configure(text="")

    def procesar_efectivo(self):
        texto_actual = self.entry_efectivo.get().replace(".", "")
        texto_limpio = ''.join(filter(str.isdigit, texto_actual))
        
        if not texto_limpio:
            entregado = self.total_num
            vueltas = 0
        else:
            entregado = int(texto_limpio)
            vueltas = entregado - self.total_num
            
        if vueltas < 0:
            self.lbl_error.configure(text=f"Falta dinero. Mínimo ${self.total_num:,}".replace(",", "."))
            return
            
        self.callback_procesar("Efectivo", self, entregado, vueltas)