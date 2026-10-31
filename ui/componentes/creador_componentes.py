import customtkinter as ctk

FUENTE_TITULOS = ("Arial", 24, "bold")
FUENTE_NORMAL = ("Arial", 12)
FUENTE_NEGRITA = ("Arial", 12, "bold")

COLOR_EXITO = "green"
COLOR_EXITO_HOVER = "darkgreen"
COLOR_FALLO = "red"
COLOR_FALLO_HOVER = "darkred"


def nuevo_frame(master, color_fondo="transparent", radio_esquinas=None, ancho=0, alto=0):
    """
    Crea un contenedor para agrupar otros elementos.
    """
    return ctk.CTkFrame(
            master, 
            fg_color = color_fondo,
            corner_radius = radio_esquinas,  
            width = ancho,
            height = alto
        )

def nuevo_label(master, texto, fuente=FUENTE_NORMAL, color_texto=None, poscicion="center"):
    """Crea una etiqueta"""
    return ctk.CTkLabel(
        master, 
        text = texto, 
        font = fuente, 
        text_color = color_texto, 
        anchor = poscicion, 
        width = 0
    )

def nueva_caja_texto(master, placeholder = ""):
    """Crea una caja de texto"""
    return ctk.CTkEntry(
        master, 
        placeholder_text = placeholder, 
        width = 250, 
        state = "normal"
    )

def nuevo_boton(master, texto, comando, fuente=FUENTE_NORMAL, color_fondo=None, color_hover=None, ancho = 140):
    """Crea un botón"""
    return ctk.CTkButton(
        master, 
        text = texto, 
        command = comando, 
        font = fuente, 
        fg_color = color_fondo, 
        hover_color = color_hover, 
        state = "normal", 
        width = ancho
    )


def nuevo_modal(master, titulo, ancho, alto):
    """Fábrica para crear ventanas secundarias (pop-ups) centradas y bloqueantes."""
    modal = ctk.CTkToplevel(master)
    modal.title(titulo)
    
    modal.update_idletasks()
    ancho_pantalla = modal.winfo_screenwidth()
    alto_pantalla = modal.winfo_screenheight()
    x = (ancho_pantalla // 2) - (ancho // 2)
    y = (alto_pantalla // 2) - (alto // 2)
    
    modal.geometry(f"{ancho}x{alto}+{x}+{y}")
    
    modal.transient(master.winfo_toplevel())
    modal.grab_set()
    
    return modal