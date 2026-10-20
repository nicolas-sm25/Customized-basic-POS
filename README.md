# POS TIENDA 

Sistema de Punto de Venta (POS) ligero y offline, principalmente diseñado para la gestion de la tienda de mi tia en Sasaima, Cundinamarca.

## Características Principales (En desarrollo)

* **Interfaz Moderna y Sencilla:** Diseñada con CustomTkintet para ser lo mas intuitiva posible
* **Gestión de Inventario:** Creación, lectura y actualización de productos alojados en una base de datos local (SQLite), con soporte para códigos de barras con un dispositivo Plug and Play
* **Cuentas Abiertas (Mesas):** Permite manejar varias ventas de forma simultánea.

## Arquitectura y Tecnologías

El proyecto está estructurado bajo el patrón de **Arquitectura de 3 Capas (Three-Tier)** para garantizar escalabilidad y un mantenimiento limpio:

* **UI (Interfaz de usuario):** `customtkinter`
* **BLL (Lógica de Negocio):** Controladores y gestores en Python puro.
* **DAL (Acceso a Datos):** `SQLAlchemy` (ORM) y `SQLite`.

## Estructura del Proyecto

```text
Customized-basic-POS/
├── bll/                    # Business Logic Layer (Lógica y validaciones)
├── dal/                    # Data Access Layer (Modelos y conexión a BD)
│   ├── modelos/            # Clases del ORM
│   └── conexion_DB.py      # Motor de la base de datos
├── ui/                     # User Interface (Vistas y componentes)
├── datos/                  # Carpeta auto-generada donde reside la base de datos
├── main.py                 # Punto de entrada de la aplicación
├── requirements.txt        # Dependencias del proyecto
└── README.md               # Documentación
```

## Instalación y uso

(Se especificará al terminar el proyecto)


## Autor

Desarrollado por Nicolás Soriano Medina - Estudiante de Ingeniería de Sistemas (A la fecha en 4to semestre ._.) (Universidad Distrital Francisco José de Caldas).