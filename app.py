from flask import Flask, request, redirect, render_template, session
import sqlite3
import os

app = Flask(__name__, template_folder=".")

app.secret_key = "clave_secreta"  # Necesario para manejar sesiones

# Crear la base de datos si no existe
def crear_bd():
    conexion = sqlite3.connect("database.db")
    cursor = conexion.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            correo TEXT UNIQUE NOT NULL,
            contraseña TEXT NOT NULL
        )
    """)
    conexion.commit()
    conexion.close()

crear_bd()

# Ruta para la página principal
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para registro (GET para mostrar, POST para procesar)
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form['nombre']
        correo = request.form['correo']
        contraseña = request.form['contraseña']

        conexion = sqlite3.connect("database.db")
        cursor = conexion.cursor()
        cursor.execute("INSERT INTO usuarios (nombre, correo, contraseña) VALUES (?, ?, ?)", 
                    (nombre, correo, contraseña))
        conexion.commit()
        conexion.close()

        return redirect('/login')  # Redirige al login después del registro
    
    return render_template('registro.html')  # Si es GET, muestra el formulario

# Ruta para login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form['correo']
        contraseña = request.form['contraseña']

        conexion = sqlite3.connect("database.db")
        cursor = conexion.cursor()
        cursor.execute("SELECT id, nombre FROM usuarios WHERE correo = ? AND contraseña = ?", (correo, contraseña))
        usuario = cursor.fetchone()
        conexion.close()

        if usuario:
            session['usuario'] = usuario[1]  # Guarda el nombre del usuario en la sesión
            return redirect('/home')  # Redirige a home.html
        else:
            return render_template('login.html', mensaje_error="Usuario o contraseña incorrectos")

    return render_template('login.html')  # Si es GET, muestra el formulario

# Ruta para mostrar home.html solo si el usuario ha iniciado sesión
@app.route('/home')
def home():
    if 'usuario' in session:  # Verifica si hay un usuario autenticado
        return render_template('home.html', usuario=session['usuario']) 
    else:
        return redirect('/login')  # Si no ha iniciado sesión, lo manda al login

# Ruta para cerrar sesión
@app.route('/index')
def logout():
    session.pop('usuario', None)  # Elimina el usuario de la sesión
    return redirect('/')  # Redirige a la página principal (index)

# Ruta para ver usuarios registrados (solo para administración)
@app.route('/admin/usuarios')
def ver_usuarios():
    if 'usuario' not in session:  # Si no hay sesión iniciada, redirige al login
        return redirect('/login')
        
    conexion = sqlite3.connect("database.db")
    cursor = conexion.cursor()
    
    # Obtener información de la estructura de la tabla
    cursor.execute("PRAGMA table_info(usuarios)")
    estructura = cursor.fetchall()
    
    # Obtener todos los usuarios
    cursor.execute("SELECT * FROM usuarios")
    usuarios = cursor.fetchall()
    
    # Obtener nombres de columnas
    nombres_columnas = [columna[1] for columna in estructura]
    
    conexion.close()
    
    return render_template('usuarios.html', 
                         usuarios=usuarios, 
                         estructura=estructura,
                         nombres_columnas=nombres_columnas)

if __name__ == '__main__':
    # Configuración para desarrollo con recarga automática
    app.run(
        host='127.0.0.1',  # Localhost
        port=5000,         # Puerto por defecto
        debug=True,        # Modo debug activado
        use_reloader=True  # Recargador automático activado
    )
