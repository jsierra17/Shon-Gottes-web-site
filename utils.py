"""
Utilidades para la aplicación
Incluye funciones de seguridad, validación y helpers
"""
import re
import secrets
import string
from datetime import datetime, timedelta
import bcrypt
from email_validator import validate_email, EmailNotValidError

def hash_password(password):
    """
    Genera un hash seguro de la contraseña usando bcrypt
    
    Args:
        password (str): Contraseña en texto plano
        
    Returns:
        str: Hash de la contraseña
    """
    # Generar salt y hash de la contraseña
    salt = bcrypt.gensalt()  # Genera un salt aleatorio
    password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)  # Hash de la contraseña
    return password_hash.decode('utf-8')  # Convertir a string para almacenar en BD

def verify_password(password, password_hash):
    """
    Verifica si una contraseña coincide con su hash
    
    Args:
        password (str): Contraseña en texto plano
        password_hash (str): Hash almacenado en la base de datos
        
    Returns:
        bool: True si la contraseña es correcta, False en caso contrario
    """
    try:
        # Verificar si la contraseña coincide con el hash
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    except Exception as e:
        print(f"Error verificando contraseña: {e}")
        return False

def validate_email_address(email):
    """
    Valida si un email tiene formato correcto y existe
    
    Args:
        email (str): Dirección de email a validar
        
    Returns:
        tuple: (bool, str) - (es_válido, mensaje_error)
    """
    try:
        # Validar formato y existencia del email
        valid = validate_email(email)
        return True, "Email válido"
    except EmailNotValidError as e:
        return False, f"Email inválido: {str(e)}"

def validate_password_strength(password):
    """
    Valida la fortaleza de una contraseña
    
    Args:
        password (str): Contraseña a validar
        
    Returns:
        tuple: (bool, str) - (es_válida, mensaje_error)
    """
    if len(password) < 8:
        return False, "La contraseña debe tener al menos 8 caracteres"
    
    if not re.search(r"[A-Z]", password):
        return False, "La contraseña debe contener al menos una letra mayúscula"
    
    if not re.search(r"[a-z]", password):
        return False, "La contraseña debe contener al menos una letra minúscula"
    
    if not re.search(r"\d", password):
        return False, "La contraseña debe contener al menos un número"
    
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "La contraseña debe contener al menos un carácter especial"
    
    return True, "Contraseña válida"

def generate_reset_token():
    """
    Genera un token seguro para recuperación de contraseña
    
    Returns:
        str: Token aleatorio seguro
    """
    # Generar token de 32 caracteres con letras y números
    alphabet = string.ascii_letters + string.digits
    token = ''.join(secrets.choice(alphabet) for _ in range(32))
    return token

def sanitize_input(text):
    """
    Sanitiza texto de entrada para prevenir XSS
    
    Args:
        text (str): Texto a sanitizar
        
    Returns:
        str: Texto sanitizado
    """
    if not text:
        return ""
    
    # Remover caracteres peligrosos
    dangerous_chars = ['<', '>', '"', "'", '&', ';', '(', ')', 'script', 'javascript']
    sanitized = text
    
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, '')
    
    # Limitar longitud
    return sanitized[:255]

def format_datetime(dt):
    """
    Formatea una fecha y hora para mostrar al usuario
    
    Args:
        dt (datetime): Fecha y hora a formatear
        
    Returns:
        str: Fecha formateada
    """
    if not dt:
        return "No disponible"
    
    # Formato en español
    return dt.strftime("%d/%m/%Y %H:%M")

def is_valid_name(name):
    """
    Valida si un nombre es válido
    
    Args:
        name (str): Nombre a validar
        
    Returns:
        tuple: (bool, str) - (es_válido, mensaje_error)
    """
    if not name or len(name.strip()) < 2:
        return False, "El nombre debe tener al menos 2 caracteres"
    
    if len(name) > 50:
        return False, "El nombre no puede tener más de 50 caracteres"
    
    # Solo permitir letras, espacios y algunos caracteres especiales
    if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s\-']+$", name):
        return False, "El nombre solo puede contener letras, espacios, guiones y apostrofes"
    
    return True, "Nombre válido"

def log_activity(user_id, activity, details=""):
    """
    Registra actividad del usuario (para futuras implementaciones)
    
    Args:
        user_id (int): ID del usuario
        activity (str): Tipo de actividad
        details (str): Detalles adicionales
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] Usuario {user_id}: {activity}"
    if details:
        log_message += f" - {details}"
    
    # Por ahora solo imprimir, en el futuro se puede guardar en archivo o BD
    print(f"ACTIVIDAD: {log_message}")

def get_client_ip(request):
    """
    Obtiene la IP real del cliente
    
    Args:
        request: Objeto request de Flask
        
    Returns:
        str: IP del cliente
    """
    # Verificar headers de proxy primero
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    else:
        return request.remote_addr
