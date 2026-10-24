import customtkinter as ctk

class ConfiguracionComponentes(ctk.CTkFrame):
    """
    Clase padre para todas las vistas que contengan formularios.
    Centraliza la limpieza y el bloqueo/desbloqueo de campos.
    """
    def __init__(self, master):
        super().__init__(master)
        
        self.entradas_editables = [] 
        self.labels_estaticos = []   
        self.botones_accion = []     
        self.elementos_busqueda = [] 
        
    def habilitar(self, *elementos):
        """Habilita (estado 'normal') widgets individuales o listas de widgets."""
        for elemento in elementos:
            if isinstance(elemento, list):
                for widget in elemento:
                    widget.configure(state="normal")
            else:
                elemento.configure(state="normal")
                
    def deshabilitar(self, *elementos):
        """Deshabilita (estado 'disabled') widgets individuales o listas de widgets."""
        for elemento in elementos:
            if isinstance(elemento, list):
                for widget in elemento:
                    widget.configure(state="disabled")
            else:
                elemento.configure(state="disabled")

    def limpiar_campos(self):
        """Limpia todos los labels y cajas de texto de forma segura."""
        for label in self.labels_estaticos:
            label.configure(text="-")
            
        if self.entradas_editables:
            estado_anterior = self.entradas_editables[0].cget("state")
            self.habilitar(self.entradas_editables)
            
            for entrada in self.entradas_editables:
                entrada.delete(0, 'end')
                
                texto_placeholder = entrada.cget("placeholder_text")
                if texto_placeholder:
                    entrada.configure(placeholder_text="")
                    entrada.configure(placeholder_text=texto_placeholder)

            for entrada in self.entradas_editables:
                entrada.configure(state=estado_anterior)