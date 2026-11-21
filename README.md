# POS TIENDA (v2.0)

Sistema de Punto de Venta (POS) ligero, offline y de alto rendimiento para Windows, diseñado para agilizar la atención en mostrador y el control administrativo de comercios minoristas.

---

## Características Principales

- **Punto de Venta Ágil y Orientado al Teclado:**
  - Búsqueda instantánea por código de barras o nombre con autocompletado flotante.
  - Multiplicador rápido de cantidades (`cantidad*código`) sin perder el foco del buscador.
  - Actualización dinámica de cantidades directamente en el carrito sin necesidad de presionar `Enter`.
  - Atajos globales de operación (`F11` Guardar venta en espera, `F12` Cobrar venta).
- **Impresora Térmica y Cajón Monedero (ESC/POS):**
  - Integración nativa en Windows (`pywin32`) compatible con tirillas de **80 mm (48 columnas)** y **58 mm (32 columnas)** con corte automático de papel.
  - 4 modos de operación configurables (*Imprimir y abrir cajón*, *Solo imprimir*, *Solo abrir cajón* o *Desactivada*).
  - Personalización de encabezado y pie de recibo (NIT, dirección, teléfono y mensaje final).
  - Botón dinámico de apertura manual de cajón en el menú lateral (visible únicamente cuando hay una impresora activa).
- **Gestión Avanzada de Inventario:**
  - Tabla paginada optimizada para catálogos extensos sin pérdida de rendimiento.
  - Soporte para productos unitarios, **productos en paquete** (relación maestro-esclavo con sincronización automática) y **grupos de stock compartido** (distintos sabores o variantes con inventario unificado).
  - Vista previa de productos derivados al registrar, advertencias de costo `$0`, sección independiente para productos inhabilitados y edición avanzada (actualización de código de barras y eliminación definitiva).
- **Control de Caja, Gastos y Recuperación ante Fallos:**
  - Apertura y cierre de turno con arqueo detallado por método de pago (**Efectivo vs. Nequi**) y cálculo automático de diferencias.
  - Bloqueo de cierre de sesión o salida del programa mientras exista una caja abierta.
  - Registro de **gastos rápidos** tanto para salidas de dinero en efectivo como para bajas/mermas de inventario.
  - Gestión de pedidos en espera (guardar, recuperar o registrar pérdida).
  - **Recuperación automática de turno** ante cortes de energía o cierres inesperados del equipo.
- **Centro de Notificaciones Inteligente:**
  - Monitoreo en tiempo real de stock agotado, stock negativo, productos con costo `$0`, paquetes con base inactiva y ventas guardadas antiguas.
  - Indicador visual con alerta parpadeante en el menú lateral, filtros por prioridad e historial de alertas ignoradas.
- **Proveedores, Roles y Seguridad:**
  - Directorio de proveedores (empresa, contacto, teléfono y NIT) vinculado al inventario.
  - Control de acceso por roles (**Administrador** vs. **Vendedor**).
  - Bloqueo de doble instancia en Windows para evitar abrir el programa dos veces simultáneamente.
  - Asistente de bienvenida en instalaciones limpias para configurar el negocio y registrar al Administrador principal.
- **Personalización Visual:**
  - Configuración del nombre de la tienda, ícono de ventana (`.ico`) y logotipo del menú lateral (`.png`) directamente desde el sistema.

---

## Arquitectura y Tecnologías

El proyecto está construido bajo el patrón de **Arquitectura de 3 Capas (Three-Tier)** para garantizar modularidad y fácil mantenimiento:

- **UI (Interfaz de Usuario):** `CustomTkinter` y `Pillow` con componentes modulares reutilizables.
- **BLL (Lógica de Negocio):** Gestores independientes en Python para ventas, inventario, caja, notificaciones, usuarios, proveedores e impresión ESC/POS.
- **DAL (Acceso a Datos):** `SQLAlchemy` (ORM) y base de datos local `SQLite` con almacenamiento persistente en `%LOCALAPPDATA%` al ejecutarse compilado.

---

## Estructura del Proyecto

```text
Customized-basic-POS/
├── bll/                        # Business Logic Layer (Lógica de negocio)
│   
├── dal/                        # Data Access Layer (Persistencia)
│   └── modelos/                # Modelos ORM (productos, ventas, caja, usuarios, etc.)
│
├── ui/                         # User Interface (Interfaz gráfica)
│   ├── componentes/            # Fábrica de widgets, modales y estilos base
│   ├── modales/                # Login, bienvenida admin, cobro, cierre, gastos, etc.
│   └── vistas/                 # Pantallas principales y sub-paneles
│       └── secciones/          # Paneles de carrito, recibo y autocompletado
│  
├── .gitignore
├── main.py                     # Punto de entrada, mutex de instancia única y log de errores
├── requirements.txt            # Dependencias del proyecto
└── README.md                   # Documentación
```

---

## Instalación y Uso

### Opción 1: Instalador para Windows (Recomendado)

1. Dirígete a la sección **Releases** de este repositorio y descarga **`Instalador_POS_v2.0.exe`**.
2. Ejecuta el instalador (no requiere tener Python instalado).
3. Al finalizar la copia de archivos, el instalador lanzará automáticamente el asistente del controlador de la impresora térmica SAT Q23T (puedes desmarcarlo si el equipo no tiene impresora).
4. Al abrir el sistema por primera vez, completa el Asistente de Bienvenida con el nombre de tu tienda y los datos del Administrador principal, y selecciona la impresora en Configuración > Impresora Térmica y Cajón Monedero.

### Opción 2: Ejecución desde Código Fuente (Desarrollo)

1. Clona el repositorio e instala las dependencias:

```bash
pip install -r requirements.txt
```

2. Ejecuta la aplicación:

```bash
python main.py
```

*(Si la base de datos está vacía, el sistema lanzará automáticamente el modal de configuración inicial para crear el primer usuario Administrador).*

---

## Compilación del Ejecutable (.exe)

Para generar la carpeta distribuible sin ventana de consola con **PyInstaller**:

```bash
pyinstaller --noconfirm --onedir --windowed --name "POS_Tienda" --paths "." --collect-all customtkinter --collect-submodules ui --collect-submodules bll --collect-submodules dal --hidden-import "win32print" --hidden-import "pywintypes" --hidden-import "sqlalchemy.dialects.sqlite" --hidden-import "PIL._tkinter_finder" main.py
```

---

## Hoja de Ruta (Próxima Versión v3.0)

* **Control de Fechas de Vencimiento:** Gestión de inventario por lotes (PEPS / FEFO) con alertas escalonadas previas al vencimiento.
* **Seguridad Avanzada:** Cifrado de contraseñas mediante hash seguro.
* **Accesibilidad Total:** Navegación 100% por teclado en todas las vistas y modales administrativos.
* **Escalabilidad y Nube:** API complementaria para concurrencia multi-caja y respaldos automáticos de la base de datos en la nube.

---

## Autor

Desarrollado por **Nicolás Soriano Medina** — Estudiante de Ingeniería de Sistemas en la Universidad Distrital Francisco José de Caldas (proyecto desarrollado estando en 4to semestre de la U :) ).
