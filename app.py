from flask import Flask, request, redirect, render_template, session
import sqlite3

app = Flask(__name__)
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
@app.route('/logout')
def logout():
    session.pop('usuario', None)  # Elimina el usuario de la sesión
    return redirect('/registro')  # Redirige al login

if __name__ == '__main__':
    app.run(debug=True)
