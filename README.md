# Sistema de Autenticación Web con Flask

Este es un sistema web de autenticación desarrollado con Flask y SQLite3, que permite a los usuarios registrarse, iniciar sesión y acceder a un área privada.

## Descripción del Proyecto

Este proyecto es una aplicación web que implementa un sistema de autenticación básico con las siguientes características:

- Registro de usuarios
- Inicio de sesión
- Área privada (home)
- Gestión de sesiones
- Base de datos SQLite3 para almacenamiento persistente

## Tecnologías Utilizadas

- Python 3.11+
- Flask (Framework web)
- SQLite3 (Base de datos)
- HTML/CSS (Frontend)
- Jinja2 (Motor de plantillas)

## Estructura del Proyecto

```
Shon-Gottes-web-site/
│
├── app.py                 # Archivo principal de la aplicación
├── database.db           # Base de datos SQLite3
├── static/              # Archivos estáticos
│   └── IMG/            # Imágenes del sitio
├── templates/          # Plantillas HTML
│   ├── home.html      # Página principal (requiere autenticación)
│   ├── login.html     # Página de inicio de sesión
│   └── registro.html  # Página de registro
└── README.md          # Este archivo
```

## Ejecución Rápida

### En Windows:
1. Doble clic en `run.bat`
2. El script automáticamente:
   - Creará un entorno virtual (si no existe)
   - Instalará las dependencias necesarias
   - Iniciará el servidor

### En Linux/Mac:
1. Abrir terminal en la carpeta del proyecto
2. Dar permisos de ejecución al script:
   ```bash
   chmod +x run.sh
   ```
3. Ejecutar el script:
   ```bash
   ./run.sh
   ```

## Ejecución Manual (Alternativa)

Si prefieres ejecutar los comandos manualmente:

1. **Crear y activar el entorno virtual**
   ```bash
   # En Windows:
   python -m venv venv
   venv\Scripts\activate

   # En Linux/Mac:
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

3. **Ejecutar la aplicación**
   ```bash
   python app.py
   ```

4. **Acceder a la Aplicación**
   - Abrir el navegador y visitar: `http://localhost:5000`
   - La aplicación te redirigirá automáticamente a la página de inicio de sesión

## Funcionalidades

1. **Registro de Usuario (`/registro`)**
   - Permite a nuevos usuarios crear una cuenta
   - Campos requeridos: nombre, correo y contraseña
   - Validación de correo único

2. **Inicio de Sesión (`/login`)**
   - Autenticación mediante correo y contraseña
   - Gestión de sesiones para mantener al usuario conectado
   - Redirección a la página principal después del login exitoso

3. **Página Principal (`/home`)**
   - Acceso restringido solo para usuarios autenticados
   - Muestra el nombre del usuario conectado
   - Opción para cerrar sesión

4. **Cerrar Sesión (`/logout`)**
   - Termina la sesión del usuario
   - Redirecciona al registro

## Administración de Base de Datos

La aplicación incluye herramientas avanzadas para la gestión de la base de datos SQLite3:

### Panel de Administración

- Acceso: `http://localhost:5000/admin/usuarios`
- Muestra:
  - Lista completa de usuarios registrados
  - Estructura detallada de la base de datos
  - Información de campos y tipos de datos

### Herramienta de Migración (`db_migration.py`)

Script potente para administrar la base de datos que incluye:

1. **Gestión de Seguridad:**
   - Creación automática de copias de seguridad
   - Backups con marca de tiempo
   - Manejo seguro de errores

2. **Administración de Tablas:**
   ```python
   migration = DatabaseMigration()
   
   # Crear nueva tabla
   campos = [
       "id INTEGER PRIMARY KEY AUTOINCREMENT",
       "nombre TEXT NOT NULL"
   ]
   migration.crear_tabla('nueva_tabla', campos)
   
   # Renombrar tabla
   migration.renombrar_tabla('tabla_vieja', 'tabla_nueva')
   ```

3. **Gestión de Campos:**
   ```python
   # Agregar nuevo campo
   migration.agregar_campo('usuarios', 'telefono', 'TEXT')
   
   # Ver estructura de tabla
   migration.mostrar_estructura('usuarios')
   ```

4. **Funciones de Diagnóstico:**
   - Verificación de existencia de tablas
   - Visualización de estructura de tablas
   - Registro de cambios realizados

### Estructura Actual de la Base de Datos

```sql
CREATE TABLE usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    correo TEXT UNIQUE NOT NULL,
    contraseña TEXT NOT NULL
)
```

### Cómo Usar las Herramientas de Administración

1. **Para ver usuarios y estructura:**
   - Inicia sesión en la aplicación
   - Visita `/admin/usuarios`

2. **Para modificar la estructura:**
   - Edita `db_migration.py`
   - Descomenta y modifica los ejemplos según necesites
   - Ejecuta: `python db_migration.py`

## Actualización en GitHub

Para actualizar el repositorio en GitHub:

1. **Inicializar Git (si no está inicializado)**
   ```bash
   git init
   ```

2. **Agregar los cambios**
   ```bash
   git add .
   ```

3. **Realizar commit**
   ```bash
   git commit -m "Actualización: Sistema de autenticación completo con documentación"
   ```

4. **Actualizar el repositorio remoto**
   ```bash
   git push origin main
   ```

## Últimas Actualizaciones

### Nuevas Características
- Panel de administración para gestión de usuarios
- Sistema de migración de base de datos
- Copias de seguridad automáticas
- Interfaz mejorada con Bootstrap
- Scripts de inicio automatizados (run.bat/run.sh)

### Mejoras Técnicas
- Gestión mejorada de sesiones
- Manejo de errores más robusto
- Documentación expandida
- Estructura de proyecto organizada

## Próximas Mejoras Sugeridas

- Implementar hash de contraseñas para mayor seguridad
- Agregar recuperación de contraseña
- Mejorar la validación de formularios
- Implementar sistema de roles de usuario
- Agregar más opciones al panel de administración
- Implementar registro de actividad (logs)
- Añadir validación de correo electrónico
- Mejorar la interfaz de usuario con más características interactivas
- Añadir más funcionalidades en el área privada
- Implementar un diseño responsive más elaborado

## Contribución

Si deseas contribuir al proyecto, puedes:
1. Hacer fork del repositorio
2. Crear una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Hacer commit de tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo LICENSE para más detalles.
