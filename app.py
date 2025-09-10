"""
Aplicación principal de Shon Gottes Web Site
Sistema web de autenticación y portfolio personal con mejoras de seguridad
"""
from flask import Flask, request, redirect, render_template, session, flash, url_for, jsonify
from flask_mail import Mail
import sqlite3
import os
from datetime import datetime, timedelta

# Importar configuraciones y utilidades
from config import config
from utils import hash_password, verify_password, log_user_activity, log_security_event, get_client_ip
from forms import RegistrationForm, LoginForm, PasswordResetForm, NewPasswordForm, ContactForm
from error_handlers import configure_logging, register_error_handlers, log_database_error
from password_reset import PasswordResetManager

# Crear aplicación Flask
app = Flask(__name__)

# Configurar aplicación según el entorno
config_name = os.environ.get('FLASK_ENV', 'development')  # Entorno por defecto: development
app.config.from_object(config[config_name])  # Cargar configuración según entorno

# Configurar Flask-Mail para envío de emails
mail = Mail(app)

# Inicializar gestor de recuperación de contraseñas
password_reset_manager = PasswordResetManager(mail)

# Configurar logging y manejo de errores
configure_logging(app)
register_error_handlers(app)

# Crear la base de datos si no existe
def crear_bd():
    """
    Crea las tablas necesarias en la base de datos
    Incluye tabla de usuarios y tabla de tokens de recuperación
    """
    try:
        conexion = sqlite3.connect("database.db")
        cursor = conexion.cursor()
        
        # Crear tabla de usuarios con campos mejorados
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                correo TEXT UNIQUE NOT NULL,
                contraseña TEXT NOT NULL,
                fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
                ultimo_acceso DATETIME,
                activo BOOLEAN DEFAULT TRUE,
                intentos_login INTEGER DEFAULT 0,
                bloqueado_hasta DATETIME
            )
        """)
        
        # Crear tabla de tokens de recuperación de contraseña
        password_reset_manager.create_reset_table()
        
        conexion.commit()
        conexion.close()
        
        app.logger.info("Base de datos inicializada correctamente")
        
    except Exception as e:
        log_database_error("crear_bd", str(e))
        app.logger.error(f"Error creando base de datos: {str(e)}")

# Inicializar base de datos
crear_bd()

# Ruta para la página principal
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para registro (GET para mostrar, POST para procesar)
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    """
    Maneja el registro de nuevos usuarios
    Incluye validaciones de seguridad y hash de contraseñas
    """
    form = RegistrationForm()  # Crear formulario con validaciones
    
    if form.validate_on_submit():  # Si el formulario es válido
        try:
            # Obtener datos del formulario
            nombre = form.nombre.data.strip()  # Limpiar espacios
            correo = form.correo.data.lower().strip()  # Normalizar email
            contraseña = form.contraseña.data
            
            # Hash de la contraseña para almacenamiento seguro
            password_hash = hash_password(contraseña)
            
            # Obtener IP del cliente para logging
            ip_address = get_client_ip(request)
            
            # Insertar usuario en la base de datos
            conexion = sqlite3.connect("database.db")
            cursor = conexion.cursor()
            cursor.execute("""
                INSERT INTO usuarios (nombre, correo, contraseña, fecha_registro) 
                VALUES (?, ?, ?, ?)
            """, (nombre, correo, password_hash, datetime.now()))
            conexion.commit()
            conexion.close()
            
            # Log de actividad de seguridad
            log_security_event(
                "USER_REGISTERED",
                f"Nuevo usuario registrado: {correo}",
                ip_address
            )
            
            # Mensaje de éxito
            flash('¡Registro exitoso! Ya puedes iniciar sesión.', 'success')
            return redirect(url_for('login'))
            
        except sqlite3.IntegrityError:
            # Error si el email ya existe
            flash('Este correo electrónico ya está registrado.', 'error')
            app.logger.warning(f"Intento de registro con email duplicado: {correo}")
            
        except Exception as e:
            # Error general
            log_database_error("registro_usuario", str(e))
            flash('Error en el registro. Por favor, intenta de nuevo.', 'error')
            app.logger.error(f"Error en registro: {str(e)}")
    
    # Si hay errores de validación, se mostrarán automáticamente
    return render_template('registro.html', form=form)

# Ruta para login
@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Maneja el inicio de sesión de usuarios
    Incluye protección contra ataques de fuerza bruta y logging de seguridad
    """
    form = LoginForm()  # Crear formulario con validaciones
    
    if form.validate_on_submit():  # Si el formulario es válido
        try:
            # Obtener datos del formulario
            correo = form.correo.data.lower().strip()  # Normalizar email
            contraseña = form.contraseña.data
            
            # Obtener IP del cliente para logging
            ip_address = get_client_ip(request)
            
            # Buscar usuario en la base de datos
            conexion = sqlite3.connect("database.db")
            cursor = conexion.cursor()
            cursor.execute("""
                SELECT id, nombre, contraseña, intentos_login, bloqueado_hasta, activo 
                FROM usuarios WHERE correo = ?
            """, (correo,))
            usuario = cursor.fetchone()
            
            if usuario:
                user_id, nombre, password_hash, intentos, bloqueado_hasta, activo = usuario
                
                # Verificar si la cuenta está bloqueada
                if bloqueado_hasta and datetime.now() < datetime.fromisoformat(bloqueado_hasta):
                    flash('Tu cuenta está temporalmente bloqueada. Intenta más tarde.', 'error')
                    log_security_event(
                        "LOGIN_BLOCKED_ACCOUNT",
                        f"Intento de login en cuenta bloqueada: {correo}",
                        ip_address,
                        user_id
                    )
                    conexion.close()
                    return render_template('login.html', form=form)
                
                # Verificar si la cuenta está activa
                if not activo:
                    flash('Tu cuenta está desactivada. Contacta al administrador.', 'error')
                    log_security_event(
                        "LOGIN_INACTIVE_ACCOUNT",
                        f"Intento de login en cuenta inactiva: {correo}",
                        ip_address,
                        user_id
                    )
                    conexion.close()
                    return render_template('login.html', form=form)
                
                # Verificar contraseña
                if verify_password(contraseña, password_hash):
                    # Login exitoso
                    # Resetear intentos de login y actualizar último acceso
                    cursor.execute("""
                        UPDATE usuarios 
                        SET intentos_login = 0, ultimo_acceso = ?, bloqueado_hasta = NULL 
                        WHERE id = ?
                    """, (datetime.now(), user_id))
                    conexion.commit()
                    conexion.close()
                    
                    # Crear sesión
                    session['usuario'] = nombre
                    session['user_id'] = user_id
                    session.permanent = True  # Sesión permanente
                    
                    # Log de actividad exitosa
                    log_user_activity(user_id, "LOGIN_SUCCESS", ip_address=ip_address)
                    
                    flash(f'¡Bienvenido, {nombre}!', 'success')
                    return redirect(url_for('home'))
                    
                else:
                    # Contraseña incorrecta
                    intentos += 1
                    
                    # Bloquear cuenta después de 5 intentos fallidos
                    if intentos >= 5:
                        bloqueado_hasta = datetime.now() + timedelta(minutes=30)  # Bloqueo por 30 minutos
                        cursor.execute("""
                            UPDATE usuarios 
                            SET intentos_login = ?, bloqueado_hasta = ? 
                            WHERE id = ?
                        """, (intentos, bloqueado_hasta, user_id))
                        
                        log_security_event(
                            "ACCOUNT_LOCKED",
                            f"Cuenta bloqueada por intentos fallidos: {correo}",
                            ip_address,
                            user_id
                        )
                        flash('Demasiados intentos fallidos. Tu cuenta está bloqueada por 30 minutos.', 'error')
                    else:
                        cursor.execute("""
                            UPDATE usuarios 
                            SET intentos_login = ? 
                            WHERE id = ?
                        """, (intentos, user_id))
                        
                        log_security_event(
                            "LOGIN_FAILED",
                            f"Intento de login fallido: {correo} (intento {intentos})",
                            ip_address,
                            user_id
                        )
                        flash(f'Usuario o contraseña incorrectos. Intentos restantes: {5-intentos}', 'error')
                    
                    conexion.commit()
                    conexion.close()
                    
            else:
                # Usuario no encontrado
                log_security_event(
                    "LOGIN_USER_NOT_FOUND",
                    f"Intento de login con usuario inexistente: {correo}",
                    ip_address
                )
                flash('Usuario o contraseña incorrectos.', 'error')
            
        except Exception as e:
            log_database_error("login_usuario", str(e))
            flash('Error en el inicio de sesión. Por favor, intenta de nuevo.', 'error')
            app.logger.error(f"Error en login: {str(e)}")
    
    return render_template('login.html', form=form)

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
    """
    Cierra la sesión del usuario actual
    Incluye logging de actividad
    """
    if 'user_id' in session:
        user_id = session['user_id']
        ip_address = get_client_ip(request)
        
        # Log de actividad
        log_user_activity(user_id, "LOGOUT", ip_address=ip_address)
    
    # Limpiar sesión
    session.clear()  # Elimina toda la información de la sesión
    flash('Has cerrado sesión correctamente.', 'info')
    return redirect(url_for('index'))

# Ruta para solicitar recuperación de contraseña
@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """
    Maneja la solicitud de recuperación de contraseña
    """
    form = PasswordResetForm()  # Crear formulario
    
    if form.validate_on_submit():  # Si el formulario es válido
        email = form.correo.data.lower().strip()
        ip_address = get_client_ip(request)
        
        # Solicitar reset de contraseña
        success, message = password_reset_manager.request_password_reset(email, ip_address)
        
        if success:
            flash('Si el email existe, recibirás un enlace de recuperación.', 'info')
        else:
            flash('Error procesando la solicitud. Intenta de nuevo.', 'error')
        
        return redirect(url_for('forgot_password'))
    
    return render_template('forgot_password.html', form=form)

# Ruta para restablecer contraseña con token
@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """
    Maneja el restablecimiento de contraseña usando un token
    """
    form = NewPasswordForm()  # Crear formulario
    
    # Validar token
    is_valid, user_id, message = password_reset_manager.validate_reset_token(token)
    
    if not is_valid:
        flash(message, 'error')
        return redirect(url_for('login'))
    
    if form.validate_on_submit():  # Si el formulario es válido
        new_password = form.nueva_contraseña.data
        ip_address = get_client_ip(request)
        
        # Restablecer contraseña
        success, message = password_reset_manager.reset_password(token, new_password, ip_address)
        
        if success:
            flash('Contraseña restablecida correctamente. Ya puedes iniciar sesión.', 'success')
            return redirect(url_for('login'))
        else:
            flash(message, 'error')
    
    return render_template('reset_password.html', form=form, token=token)

# Ruta para ver usuarios registrados (solo para administración)
@app.route('/admin/usuarios')
def ver_usuarios():
    """
    Panel de administración para ver usuarios registrados
    Requiere autenticación
    """
    if 'usuario' not in session:  # Si no hay sesión iniciada, redirige al login
        return redirect(url_for('login'))
    
    try:
        conexion = sqlite3.connect("database.db")
        cursor = conexion.cursor()
        
        # Obtener información de la estructura de la tabla
        cursor.execute("PRAGMA table_info(usuarios)")
        estructura = cursor.fetchall()
        
        # Obtener todos los usuarios con información completa
        cursor.execute("""
            SELECT id, nombre, correo, fecha_registro, ultimo_acceso, activo, intentos_login
            FROM usuarios 
            ORDER BY fecha_registro DESC
        """)
        usuarios = cursor.fetchall()
        
        # Obtener nombres de columnas
        nombres_columnas = [columna[1] for columna in estructura]
        
        conexion.close()
        
        # Log de actividad de administración
        log_user_activity(session.get('user_id'), "ADMIN_VIEW_USERS")
        
        return render_template('admin/usuarios.html', 
                             usuarios=usuarios, 
                             estructura=estructura,
                             nombres_columnas=nombres_columnas)
                             
    except Exception as e:
        log_database_error("ver_usuarios_admin", str(e))
        flash('Error cargando la información de usuarios.', 'error')
        return redirect(url_for('home'))

# Ruta para contacto
@app.route('/contacto', methods=['GET', 'POST'])
def contacto():
    """
    Maneja el formulario de contacto
    """
    form = ContactForm()  # Crear formulario
    
    if form.validate_on_submit():  # Si el formulario es válido
        try:
            # Obtener datos del formulario
            nombre = form.nombre.data.strip()
            correo = form.correo.data.lower().strip()
            asunto = form.asunto.data
            mensaje = form.mensaje.data.strip()
            
            # Obtener IP del cliente
            ip_address = get_client_ip(request)
            
            # Aquí se podría enviar un email o guardar en base de datos
            # Por ahora solo logueamos la información
            app.logger.info(f"Mensaje de contacto recibido de {nombre} ({correo}): {asunto}")
            
            # Log de actividad
            log_user_activity(None, "CONTACT_FORM_SUBMITTED", 
                            f"Asunto: {asunto}", ip_address)
            
            flash('¡Mensaje enviado correctamente! Te responderemos pronto.', 'success')
            return redirect(url_for('contacto'))
            
        except Exception as e:
            app.logger.error(f"Error procesando formulario de contacto: {str(e)}")
            flash('Error enviando el mensaje. Por favor, intenta de nuevo.', 'error')
    
    return render_template('contacto.html', form=form)

if __name__ == '__main__':
    """
    Punto de entrada principal de la aplicación
    Configuración optimizada para desarrollo y producción
    """
    # Limpiar tokens expirados al iniciar
    try:
        password_reset_manager.cleanup_expired_tokens()
    except Exception as e:
        app.logger.warning(f"Error limpiando tokens expirados: {str(e)}")
    
    # Configuración del servidor según el entorno
    if app.config['DEBUG']:
        # Configuración para desarrollo
        app.logger.info("Iniciando servidor en modo DESARROLLO")
        app.run(
            host='127.0.0.1',  # Localhost
            port=5000,         # Puerto por defecto
            debug=True,        # Modo debug activado
            use_reloader=True  # Recargador automático activado
        )
    else:
        # Configuración para producción
        app.logger.info("Iniciando servidor en modo PRODUCCIÓN")
        app.run(
            host='0.0.0.0',    # Escuchar en todas las interfaces
            port=int(os.environ.get('PORT', 5000)),  # Puerto desde variable de entorno
            debug=False,       # Modo debug desactivado
            use_reloader=False # Recargador automático desactivado
        )
