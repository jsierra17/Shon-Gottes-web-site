"""
Configuración de la aplicación Flask
Maneja diferentes entornos (desarrollo, producción, testing)
"""
import os
import secrets
from dotenv import load_dotenv

# Cargar variables de entorno desde archivo .env
load_dotenv()

class Config:
    """Configuración base para todos los entornos"""
    
    # Configuración de seguridad
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)  # Clave secreta segura generada automáticamente
    
    # Configuración de base de datos
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'sqlite:///database.db'
    
    # Configuración de email para recuperación de contraseña
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')  # Tu email
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')  # Tu contraseña de aplicación
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or MAIL_USERNAME
    
    # Configuración de la aplicación
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # Límite de 16MB para archivos
    UPLOAD_FOLDER = 'static/uploads'  # Carpeta para archivos subidos
    
    # Configuración de sesiones
    PERMANENT_SESSION_LIFETIME = 3600  # Sesión expira en 1 hora
    
    # Configuración de seguridad adicional
    WTF_CSRF_ENABLED = True  # Protección CSRF habilitada
    WTF_CSRF_TIME_LIMIT = 3600  # Token CSRF válido por 1 hora

class DevelopmentConfig(Config):
    """Configuración para entorno de desarrollo"""
    DEBUG = True  # Modo debug activado
    TESTING = False  # No es entorno de testing

class ProductionConfig(Config):
    """Configuración para entorno de producción"""
    DEBUG = False  # Modo debug desactivado
    TESTING = False  # No es entorno de testing
    
    # Configuraciones adicionales para producción
    SESSION_COOKIE_SECURE = True  # Cookies seguras solo en HTTPS
    SESSION_COOKIE_HTTPONLY = True  # Cookies no accesibles desde JavaScript
    SESSION_COOKIE_SAMESITE = 'Lax'  # Protección CSRF

class TestingConfig(Config):
    """Configuración para entorno de testing"""
    TESTING = True  # Entorno de testing
    DEBUG = True  # Debug activado para testing
    DATABASE_URL = 'sqlite:///:memory:'  # Base de datos en memoria para tests
    WTF_CSRF_ENABLED = False  # CSRF deshabilitado para testing

# Diccionario de configuraciones disponibles
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig  # Configuración por defecto
}
