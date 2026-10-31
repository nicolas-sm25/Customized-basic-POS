# POS TIENDA 

Sistema de Punto de Venta (POS) ligero, offline y orientado al teclado, diseñado específicamente para la gestión eficiente del negocio.

## Características Principales

* **Interfaz Moderna y Fluida:** Desarrollada con CustomTkinter, optimizada para minimizar el uso del mouse y evitar "cursóres fantasma".
* **Gestión de Inventario Robusta:** 
  * Soporte para productos unitarios y **productos en paquete** (sistema maestro-esclavo con sincronización automática de stock).
  * Alertas visuales de stock crítico ($\le 5$ unidades).
  * Desactivación y reactivación lógica de productos con efecto en cascada para proteger el historial de ventas pasadas.
* **Flujo de Caja Avanzado:**
  * Control de apertura y cierre de caja con cálculo automático de efectivo esperado, sobrantes y faltantes.
  * Desglose detallado de rendimiento por método de pago (**Efectivo vs. Nequi**).
  * Registro de **gastos rápidos** (ej. pagos a proveedores) integrados en tiempo real al balance del día.
* **Ventas en Espera (Pedidos):** Guardar, recuperar o eliminar pedidos pendientes de forma intuitiva.
* **Sistema de Roles y Seguridad:** Control de acceso diferenciado entre **Administrador** (acceso total gerencial y de gestión) y **Vendedor** (restringido a operaciones de caja e inventario).
* **Historial Gerencial:** Módulo completo de trazabilidad de turnos anteriores con detalle de ganancias netas, costos, gastos y encargados de cada caja.
* **Configuración del Sistema:** Selector de tema visual (Dark/Light/System) y control de sesión integrada.

## Arquitectura y Tecnologías

El proyecto está estructurado bajo el patrón de **Arquitectura de 3 Capas (Three-Tier)** para garantizar modularidad y mantenibilidad:

* **UI (Interfaz de Usuario):** `customtkinter` y diseño de componentes reutilizables.
* **BLL (Lógica de Negocio):** Controladores en Python puro para manejo de stock, ventas y contabilidad.
* **DAL (Acceso a Datos):** `SQLAlchemy` (ORM) y base de datos local `SQLite`.

## Estructura del Proyecto

```text
Customized-basic-POS/
├── bll/                    # Business Logic Layer (Lógica de negocio y reglas)
├── dal/                    # Data Access Layer (Modelos ORM y conexión a BD)
│   ├── modelos/            # Tablas: productos, ventas, contabilidad_caja, usuarios, etc.
│   └── conexion_DB.py      # Motor de la base de datos
├── ui/                     # User Interface 
│   ├── vistas/             # Pantallas principales (Caja, Inventario, Historial, etc.)
│   ├── modales/            # Pop-ups de cobro, cierre, gastos, login, etc.
│   └── componentes/        # Fábrica de modales y componentes visuales
├── datos/                  # Carpeta auto-generada con la base de datos SQLite
├── main.py                 # Punto de entrada de la aplicación
├── crear_usuario.py        # Script auxiliar para registro de usuarios por consola
├── requirements.txt        # Dependencias del proyecto
└── README.md               # Documentación
```

## Instalación y uso

1. Clona el repositorio e instala las dependencias:
   
      - pip install -r requirements.txt

2. Crea tu primer usuario Administrador ejecutando en la terminal:

      - py crear_usuario.py "Tu Nombre" "admin" "tu_contraseña" "Administrador"

3. Ejecuta el sistema:

      - py main.py

## Compilación del Ejecutable (.exe)
Para generar el archivo ejecutable portable sin consola:

 - python -m PyInstaller --noconsole --onefile --name="POS_MiTienda" main.py


## Autor

Desarrollado por Nicolás Soriano Medina - Estudiante de Ingeniería de Sistemas (A la fecha du publicación del proyecto en 4to semestre ._.) (Universidad Distrital Francisco José de Caldas).