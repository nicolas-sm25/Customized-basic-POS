import customtkinter as ctk
from bll.gestor_productos import buscar_productos_por_nombre
from ui.componentes.creador_componentes import nuevo_boton

class PanelAutocompletado:
    """
    Controlador reutilizable para inyectar búsqueda difusa y scroll fluido 
    con teclado a cualquier Entry de CustomTkinter.
    """
    def __init__(self, entry_widget, frame_padre, frame_before, callback_seleccion):
        self.entry = entry_widget
        self.callback = callback_seleccion
        self.frame_padre = frame_padre
        self.frame_before = frame_before
        
        self.frame_sugerencias = ctk.CTkScrollableFrame(self.frame_padre, fg_color="#2b2b2b", height=120)
        self.indice_sugerencia = -1
        self.botones_sugerencia = []
        self.sugerencias_actuales = []

        self.entry.bind("<KeyRelease>", self.mostrar_sugerencias)
        self.entry.bind("<Up>", self.navegar_arriba)
        self.entry.bind("<Down>", self.navegar_abajo)
        
    def navegar_arriba(self, event):
        self.mover_seleccion(-1)
        return "break"

    def navegar_abajo(self, event):
        self.mover_seleccion(1)
        return "break"

    def mover_seleccion(self, paso):
        if not self.botones_sugerencia: return

        if self.indice_sugerencia >= 0:
            self.botones_sugerencia[self.indice_sugerencia].configure(fg_color="#3b3b3b")
            
        self.indice_sugerencia += paso
        total_items = len(self.botones_sugerencia)

        if self.indice_sugerencia >= total_items:
            self.indice_sugerencia = 0
        elif self.indice_sugerencia < 0:
            self.indice_sugerencia = total_items - 1

        self.botones_sugerencia[self.indice_sugerencia].configure(fg_color="#87868A")

        try:
            items_visibles = 6 
            if total_items > items_visibles:
                canvas = self.frame_sugerencias._parent_canvas
                pos_actual = canvas.yview()[0]

                if self.indice_sugerencia < items_visibles:
                    destino = 0.0
                else:
                    destino = (self.indice_sugerencia - (items_visibles - 1)) / (total_items - items_visibles)
                
                if hasattr(self, '_anim_scroll_id') and self._anim_scroll_id:
                    self.entry.after_cancel(self._anim_scroll_id)
                
                self._animar_scroll_fluido(canvas, pos_actual, destino, pasos=6, actual=1)
        except Exception:
            pass

    def _animar_scroll_fluido(self, canvas, inicio, fin, pasos, actual):
        if actual <= pasos:
            posicion = inicio + (fin - inicio) * (actual / pasos)
            canvas.yview_moveto(posicion)
            self._anim_scroll_id = self.entry.after(8, lambda: self._animar_scroll_fluido(canvas, inicio, fin, pasos, actual + 1))

    def mostrar_sugerencias(self, event):
        if event.keysym in ['Up', 'Down', 'Return']: return 
            
        criterio = self.entry.get().strip()

        if "*" in criterio:
            partes = criterio.split("*", 1)
            criterio_busqueda = partes[1].strip() if len(partes) > 1 else ""
        else:
            criterio_busqueda = criterio

        if not criterio_busqueda or criterio_busqueda.isdigit():
            self.ocultar()
            return

        if len(criterio_busqueda) >= 2:
            resultados = buscar_productos_por_nombre(criterio_busqueda)
            activos = [p for p in resultados if p.get('activo', True)][:15]
            
            if activos:
                target = self.frame_before._parent_frame if hasattr(self.frame_before, '_parent_frame') else self.frame_before
                
                try:
                    self.frame_sugerencias.pack(fill="x", pady=(0, 10), before=target)
                except Exception:
                    self.frame_sugerencias.pack(fill="x", pady=(0, 10))
                    
                for w in self.frame_sugerencias.winfo_children(): w.destroy()
                
                self.sugerencias_actuales = activos
                self.botones_sugerencia = []
                self.indice_sugerencia = -1

                try:
                    self.frame_sugerencias._parent_canvas.yview_moveto(0)
                except Exception:
                    pass
                
                for prod in activos:
                    texto = f"{prod['nombre']} - ${int(prod['precio_venta']):,}".replace(",", ".")
                    btn = nuevo_boton(self.frame_sugerencias, texto, comando=lambda p=prod: self.seleccionar(p), color_fondo="#3b3b3b", color_hover="#555555")
                    btn.pack(fill="x", pady=2, padx=5)
                    self.botones_sugerencia.append(btn)
            else:
                self.ocultar()

    def seleccionar(self, producto):
        self.ocultar()
        self.callback(producto)
        
    def ocultar(self):
        self.frame_sugerencias.pack_forget()
        self.botones_sugerencia = []
        self.indice_sugerencia = -1
        
    def procesar_enter(self):
        """Método externo que debe ser llamado por la vista cuando el usuario presiona Enter."""
        if self.indice_sugerencia >= 0 and self.sugerencias_actuales:
            producto = self.sugerencias_actuales[self.indice_sugerencia]
            self.seleccionar(producto)
            return True
        self.ocultar()
        return False