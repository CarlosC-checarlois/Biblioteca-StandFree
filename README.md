# StandFree: Cafetería-Librería Web Prototype

StandFree es una plataforma web que combina la experiencia cultural de una cafetería con el mundo literario. Este prototipo busca ofrecer una experiencia visual atractiva y funcional, implementada con Django para el backend y tecnologías modernas como HTML, CSS y JavaScript para el frontend.

---

## Descripción del Proyecto

StandFree permite a los usuarios explorar productos gastronómicos y literarios, integrando funcionalidades básicas de navegación, visualización de productos y un carrito de compras estático. El proyecto se centra en la creación de un prototipo funcional y escalable, con un diseño adaptativo que brinda una experiencia fluida en múltiples plataformas.

---

## Características Principales

### Frontend:
- **Interfaz visual dinámica:**
  - Diseño atractivo y consistente, basado en HTML y CSS.
  - Interacciones básicas con JavaScript, incluyendo un modo oscuro y modales.
- **Búsqueda de productos:**
  - Barra de búsqueda con filtros por nombre, precio o categoría.
- **Diseño responsivo:**
  - Adaptabilidad garantizada para dispositivos móviles y escritorios.

### Backend:
- **Base de datos relacional:**
  - Modelos definidos en Django para gestionar libros, productos gastronómicos, categorías y carrito de compras.
- **Integración dinámica:**
  - Conexión entre vistas y modelos para mostrar datos en tiempo real.
- **Soporte para productos múltiples:**
  - Gestión de libros y carta gastronómica con detalles personalizados.

---

## Estructura del Proyecto

StandFree/
│
├── webapp/
│   ├── migrations/         # Archivos de migración de la base de datos
│   ├── static/
│   │   ├── css/            # Archivos de estilo CSS
│   │   ├── images/         # Imágenes del frontend
│   │   ├── js/             # Archivos JavaScript
│   │   └── videos/         # Videos utilizados en el proyecto
│   ├── templates/
│   │   ├── cabezal.html    # Plantilla base
│   │   ├── libros.html     # Página de libros
│   │   ├── cartas.html     # Página de la carta
│   │   ├── contacto.html   # Página de contacto
│   │   └── panel.html      # Panel de usuario
│   ├── models.py           # Modelos de la base de datos
│   ├── views.py            # Lógica de vistas
│   └── urls.py             # Rutas del proyecto
│
├── db.sqlite3              # Base de datos SQLite (desarrollo)
├── manage.py               # Administrador de Django
└── README.md               # Documentación del proyecto

---

## Requisitos del Proyecto

### Tecnologías Utilizadas:
- **Frontend:**
  - HTML5, CSS3
  - JavaScript
- **Backend:**
  - Django Framework (Python 3.9+)
- **Base de Datos:**
  - SQLite (desarrollo; puede migrarse a PostgreSQL o MySQL en producción)

### Requisitos de Instalación:
- Python 3.9+
- Pip (gestor de paquetes de Python)
- Entorno virtual recomendado (venv o similar)

---

## Instalación

1. **Clonar el Repositorio:**
   git clone https://github.com/usuario/StandFree.git
   cd StandFree

2. **Crear un Entorno Virtual:**
   python -m venv venv
   source venv/bin/activate  # Linux/MacOS
   venv\Scripts\activate     # Windows

3. **Instalar Dependencias:**
   pip install -r requirements.txt

4. **Configurar la Base de Datos:**
   python manage.py migrate

5. **Iniciar el Servidor:**
   python manage.py runserver

Accede al sitio en `http://127.0.0.1:8000/`.

---

## Contribuciones

¡Las contribuciones son bienvenidas! Si deseas colaborar:
1. Haz un fork del repositorio.
2. Crea una nueva rama:
   git checkout -b feature/nueva-funcionalidad
3. Haz commit de tus cambios:
   git commit -m 'Añadir nueva funcionalidad'
4. Haz push a la rama:
   git push origin feature/nueva-funcionalidad
5. Abre un Pull Request.

### Base de datos
Se muestra el modelo fisico de la base de datos del proyecto Biblioteca StandFree

## Anexos

| **Pantalla de Inicio**                                                                      | **Pantalla de Quienes Somos**                                                                                                |
|---------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------|
| <img src="documentacion/Base_De_Datos_PDM_BIBLIOTECA_STAND_FREE.png" alt="Pantalla de Inicio" style="max-width: 300px; height: auto;"> | <img src="documentacion/DIAGRAMA_CLASES_BIBLIOTECA_STAND_FREE.png" alt="Pantalla de Quienes Somos" style="max-width: 300px; height: auto;"> |

| **Más Información**                                                                      |
|------------------------------------------------------------------------------------------|
| <img src="documentacion/DIAGRAMA_JVSCRIPT_FRONTEND_BIBLIOTECA_STAND_FREE.png" alt="Más Información" style="max-width: 300px; height: auto;"> |
## Contacto

Desarrollado por **Carlos Constante**.
---

## Licencia

Este proyecto está licenciado bajo la [MIT License](https://opensource.org/licenses/MIT).

---

¡Gracias por explorar la Biblioteca StandFree! ☕📚
