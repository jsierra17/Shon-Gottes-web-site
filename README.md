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

## Base de Datos

La aplicación utiliza SQLite3 como sistema de gestión de base de datos, lo cual facilita la portabilidad y no requiere configuración adicional de servidores. La estructura de la base de datos incluye:

```sql
CREATE TABLE usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    correo TEXT UNIQUE NOT NULL,
    contraseña TEXT NOT NULL
)
```

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

## Próximas Mejoras Sugeridas

- Implementar hash de contraseñas para mayor seguridad
- Agregar recuperación de contraseña
- Mejorar la validación de formularios
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
