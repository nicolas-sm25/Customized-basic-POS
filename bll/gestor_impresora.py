import json
import os
from datetime import datetime
from dal.conexion_DB import CARPETA_CONFIG

try:
    import win32print
    WIN32_DISPONIBLE = True
except ImportError:
    WIN32_DISPONIBLE = False

CONFIG_PATH = os.path.join(CARPETA_CONFIG, "config.json")

ESC_INIT = b"\x1b\x40"
ESC_CODEPAGE_850 = b"\x1b\x74\x02"      
ESC_ALIGN_LEFT = b"\x1b\x61\x00"
ESC_ALIGN_CENTER = b"\x1b\x61\x01"
ESC_ALIGN_RIGHT = b"\x1b\x61\x02"
ESC_BOLD_ON = b"\x1b\x45\x01"
ESC_BOLD_OFF = b"\x1b\x45\x00"
GS_SIZE_NORMAL = b"\x1d\x21\x00"
GS_SIZE_DOUBLE = b"\x1d\x21\x11"         
GS_CUT_PARTIAL = b"\x1d\x56\x41\x03"    
ESC_OPEN_DRAWER = b"\x1b\x70\x00\x19\xfa"  

MODOS_IMPRESORA = {
    "ambos": "Imprimir recibos y abrir cajón",
    "solo_imprimir": "Solo imprimir recibos",
    "solo_cajon": "Solo abrir cajón monedero",
    "desactivada": "Desactivada"
}

CONFIG_IMPRESORA_DEFECTO = {
    "nombre_impresora": "",
    "modo": "desactivada",
    "ancho_papel": 48,
    "nit": "",
    "direccion": "",
    "telefono": "",
    "mensaje_pie": "¡Gracias por su compra! Vuelva pronto"
}


def listar_impresoras_windows():
    """Retorna la lista de nombres de impresoras instaladas en Windows."""
    if not WIN32_DISPONIBLE:
        return []
    try:
        flags = win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS
        impresoras = win32print.EnumPrinters(flags)
        return [imp[2] for imp in impresoras if len(imp) > 2]
    except Exception:
        return []


def cargar_config_completa():
    """Lee config.json completo manteniendo compatibilidad con nombre_tienda."""
    cfg = {"nombre_tienda": "TIENDA"}
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    cfg.update(data)
        except Exception:
            pass

    imp_guardada = cfg.get("impresora", {})
    imp_final = dict(CONFIG_IMPRESORA_DEFECTO)
    if isinstance(imp_guardada, dict):
        imp_final.update(imp_guardada)
    cfg["impresora"] = imp_final
    return cfg


def cargar_config_impresora():
    """Retorna únicamente el diccionario de configuración de la impresora."""
    return cargar_config_completa()["impresora"]

def impresora_esta_configurada():
    """Retorna True si hay una impresora seleccionada y el modo no está desactivado."""
    cfg_imp = cargar_config_impresora()
    nombre = (cfg_imp.get("nombre_impresora") or "").strip()
    modo = cfg_imp.get("modo", "desactivada")
    return bool(nombre) and nombre != "Sin impresora" and modo != "desactivada"

def guardar_config_impresora(datos_impresora):
    """Guarda los ajustes de la impresora en config.json sin alterar nombre_tienda."""
    try:
        cfg = cargar_config_completa()
        cfg["impresora"].update(datos_impresora)
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False)
        return True, "Configuración de impresora guardada correctamente."
    except Exception as e:
        return False, f"Error al guardar configuración: {str(e)}"


def _enviar_raw_impresora(nombre_impresora, datos_bytes):
    """Envía bytes ESC/POS crudos al spooler de Windows sin bloquear el POS si falla."""
    if not WIN32_DISPONIBLE:
        return False, "Falta la librería 'pywin32'. Instala con: pip install pywin32"
    if not nombre_impresora or nombre_impresora == "Sin impresora":
        return False, "No hay ninguna impresora seleccionada en Configuración."

    try:
        h_printer = win32print.OpenPrinter(nombre_impresora)
        try:
            win32print.StartDocPrinter(h_printer, 1, ("POS Ticket", None, "RAW"))
            try:
                win32print.StartPagePrinter(h_printer)
                win32print.WritePrinter(h_printer, datos_bytes)
                win32print.EndPagePrinter(h_printer)
            finally:
                win32print.EndDocPrinter(h_printer)
        finally:
            win32print.ClosePrinter(h_printer)
        return True, "Enviado correctamente."
    except Exception as e:
        return False, f"No se pudo comunicar con '{nombre_impresora}': {str(e)}"


def abrir_cajon_monedero(forzar_manual=False, nombre_impresora_override=None):
    """
    Envía el pulso RJ11 para abrir el cajón monedero.
    - En eventos automáticos (apertura, cierre, gasto, venta efectivo) actúa solo si modo es 'ambos' o 'solo_cajon'.
    - En disparo manual (botón Abrir Cajón o Probar Cajón) actúa mientras no esté 'desactivada'.
    """
    cfg_imp = cargar_config_impresora()
    modo = cfg_imp.get("modo", "desactivada")
    impresora = nombre_impresora_override or cfg_imp.get("nombre_impresora", "")

    if nombre_impresora_override is None:
        if modo == "desactivada":
            return False, "La impresora y el cajón están desactivados en Configuración."
        if not forzar_manual and modo not in ("ambos", "solo_cajon"):
            return False, "El modo actual no abre el cajón automáticamente."

    payload = ESC_INIT + ESC_OPEN_DRAWER
    return _enviar_raw_impresora(impresora, payload)


def _txt(texto):
    """Codifica texto a CP850 para tildes y ñ en impresoras térmicas."""
    return texto.encode("cp850", errors="replace")


def _formato_pesos(valor):
    return f"${int(round(valor)):,}".replace(",", ".")


def _construir_bytes_recibo(
    nombre_tienda,
    cfg_imp,
    venta_id,
    fecha_str,
    cajero,
    metodo_pago,
    items,
    total,
    recibido=0,
    cambio=0,
    cliente=None,
    abrir_cajon=False
):
    ancho = int(cfg_imp.get("ancho_papel", 48))
    sep_doble = "=" * ancho + "\n"
    sep_simple = "-" * ancho + "\n"

    buf = bytearray()
    buf += ESC_INIT + ESC_CODEPAGE_850

    if abrir_cajon:
        buf += ESC_OPEN_DRAWER

    # --- ENCABEZADO ---
    buf += ESC_ALIGN_CENTER
    buf += _txt(sep_doble)
    buf += ESC_BOLD_ON + GS_SIZE_DOUBLE
    buf += _txt(f"{nombre_tienda.upper()}\n")
    buf += GS_SIZE_NORMAL + ESC_BOLD_OFF

    nit = cfg_imp.get("nit", "").strip()
    direccion = cfg_imp.get("direccion", "").strip()
    telefono = cfg_imp.get("telefono", "").strip()

    if nit:
        buf += _txt(f"NIT: {nit}\n")
    if direccion:
        buf += _txt(f"{direccion}\n")
    if telefono:
        buf += _txt(f"Tel: {telefono}\n")

    buf += _txt(sep_doble)

    # --- METADATOS DEL RECIBO ---
    buf += ESC_ALIGN_LEFT
    num_recibo = f"{int(venta_id):05d}" if isinstance(venta_id, int) else str(venta_id)
    buf += _txt(f"Recibo #: {num_recibo}\n")
    buf += _txt(f"Fecha:    {fecha_str}\n")
    if cajero:
        buf += _txt(f"Cajero:   {cajero}\n")
    if cliente:
        buf += _txt(f"Cliente:  {cliente}\n")
    buf += _txt(f"Pago:     {metodo_pago}\n")
    buf += _txt(sep_simple)

    # --- TABLA DE PRODUCTOS ---
    buf += ESC_BOLD_ON
    if ancho >= 48:
        buf += _txt(f"{'CANT':>4} {'DESCRIPCION':<23} {'P.UNIT':>9} {'SUBTOT':>9}\n")
    else:
        buf += _txt(f"{'CNT':>3} {'PRODUCTO':<13} {'UNIT':>6} {'SUBT':>7}\n")
    buf += ESC_BOLD_OFF
    buf += _txt(sep_simple)

    for it in items:
        cant = str(it.get("cantidad", 1))
        nombre = str(it.get("nombre", "Producto")).strip()
        p_unit = f"{int(round(it.get('precio_venta', 0))):,}".replace(",", ".")
        subtot = f"{int(round(it.get('subtotal', 0))):,}".replace(",", ".")

        if ancho >= 48:
            linea = f"{cant:>4} {nombre[:23]:<23} {p_unit:>9} {subtot:>9}\n"
            buf += _txt(linea)
            if len(nombre) > 23:
                buf += _txt(f"     {nombre[23:46]}\n")
        else:
            linea = f"{cant:>3} {nombre[:13]:<13} {p_unit:>6} {subtot:>7}\n"
            buf += _txt(linea)
            if len(nombre) > 13:
                buf += _txt(f"    {nombre[13:26]}\n")

    buf += _txt(sep_simple)

    # --- TOTALES ---
    buf += ESC_BOLD_ON
    etiqueta_total = "TOTAL A PAGAR:"
    val_total = _formato_pesos(total)
    espacios_tot = max(1, ancho - len(etiqueta_total) - len(val_total))
    buf += _txt(f"{etiqueta_total}{' ' * espacios_tot}{val_total}\n")
    buf += ESC_BOLD_OFF

    if metodo_pago == "Efectivo" and recibido > 0:
        etq_rec = "Recibido:"
        val_rec = _formato_pesos(recibido)
        esp_rec = max(1, ancho - len(etq_rec) - len(val_rec))
        buf += _txt(f"{etq_rec}{' ' * esp_rec}{val_rec}\n")

        etq_cam = "Cambio / Vueltos:"
        val_cam = _formato_pesos(cambio)
        esp_cam = max(1, ancho - len(etq_cam) - len(val_cam))
        buf += _txt(f"{etq_cam}{' ' * esp_cam}{val_cam}\n")

    # --- PIE DE RECIBO ---
    buf += ESC_ALIGN_CENTER
    buf += _txt(sep_doble)
    mensaje_pie = cfg_imp.get("mensaje_pie", "").strip()
    if mensaje_pie:
        buf += _txt(f"{mensaje_pie}\n")
    buf += _txt(sep_doble)

    # --- CORTE DE PAPEL ---
    buf += GS_CUT_PARTIAL
    return bytes(buf)


def procesar_impresion_venta(venta_id, items, total, metodo_pago, recibido=0, cambio=0, cajero="", cliente=None):
    """
    Evalúa el modo configurado tras cobrar una venta:
    - 'ambos': imprime recibo y abre cajón si fue en Efectivo.
    - 'solo_imprimir': imprime recibo sin abrir cajón.
    - 'solo_cajon': no imprime recibo y abre cajón si fue en Efectivo.
    - 'desactivada': no hace nada.
    """
    cfg = cargar_config_completa()
    nombre_tienda = cfg.get("nombre_tienda", "TIENDA")
    cfg_imp = cfg["impresora"]
    modo = cfg_imp.get("modo", "desactivada")
    impresora = cfg_imp.get("nombre_impresora", "")

    if modo == "desactivada":
        return True, "Impresora desactivada."

    es_efectivo = (metodo_pago == "Efectivo")

    if modo == "solo_cajon":
        if es_efectivo:
            return abrir_cajon_monedero(forzar_manual=False)
        return True, "Pago por Nequi: cajón no requerido."

    debe_abrir_cajon = (modo == "ambos" and es_efectivo)
    fecha_str = datetime.now().strftime("%d/%m/%Y %I:%M %p")

    bytes_ticket = _construir_bytes_recibo(
        nombre_tienda=nombre_tienda,
        cfg_imp=cfg_imp,
        venta_id=venta_id,
        fecha_str=fecha_str,
        cajero=cajero,
        metodo_pago=metodo_pago,
        items=items,
        total=total,
        recibido=recibido,
        cambio=cambio,
        cliente=cliente,
        abrir_cajon=debe_abrir_cajon
    )
    return _enviar_raw_impresora(impresora, bytes_ticket)


def imprimir_ticket_prueba(config_override=None):
    """Imprime un recibo de prueba con corte automático usando los datos actuales del formulario."""
    cfg = cargar_config_completa()
    nombre_tienda = cfg.get("nombre_tienda", "TIENDA")
    cfg_imp = dict(cfg["impresora"])
    if config_override:
        cfg_imp.update(config_override)

    items_demo = [
        {"cantidad": 2, "nombre": "Gomitas Trululu Fresa", "precio_venta": 1500, "subtotal": 3000},
        {"cantidad": 1, "nombre": "Coca Cola 1.5L", "precio_venta": 5500, "subtotal": 5500},
        {"cantidad": 3, "nombre": "Galletas Festival", "precio_venta": 1200, "subtotal": 3600},
    ]

    bytes_ticket = _construir_bytes_recibo(
        nombre_tienda=nombre_tienda,
        cfg_imp=cfg_imp,
        venta_id="PRUEBA",
        fecha_str=datetime.now().strftime("%d/%m/%Y %I:%M %p"),
        cajero="Administrador",
        metodo_pago="Efectivo",
        items=items_demo,
        total=12100,
        recibido=20000,
        cambio=7900,
        abrir_cajon=False
    )
    return _enviar_raw_impresora(cfg_imp.get("nombre_impresora", ""), bytes_ticket)