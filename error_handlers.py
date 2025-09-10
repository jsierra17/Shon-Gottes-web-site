"""
Manejo de errores y logging para la aplicación
Incluye páginas de error personalizadas y sistema de logging
"""
import logging
import os
from datetime import datetime
from flask import render_template, request, current_app
from utils import get_client_ip, log_activity

def configure_logging(app):
    """
    Configura el sistema de logging para la aplicación
    
    Args:
        app: Instancia de la aplicación Flask
    """
    # Crear directorio de logs si no existe
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Configurar nivel de logging según el entorno
    if app.config['DEBUG']:
        log_level = logging.DEBUG  # Nivel debug para desarrollo
    else:
        log_level = logging.INFO   # Nivel info para producción
    
    # Configurar formato de logging
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    )
    
    # Configurar archivo de logging
    file_handler = logging.FileHandler('logs/app.log', encoding='utf-8')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(log_level)
    
    # Configurar logging de errores
    error_handler = logging.FileHandler('logs/error.log', encoding='utf-8')
    error_handler.setFormatter(formatter)
    error_handler.setLevel(logging.ERROR)
    
    # Configurar logging de seguridad
    security_handler = logging.FileHandler('logs/security.log', encoding='utf-8')
    security_handler.setFormatter(formatter)
    security_handler.setLevel(logging.WARNING)
    
    # Agregar handlers a la aplicación
    app.logger.addHandler(file_handler)
    app.logger.addHandler(error_handler)
    app.logger.addHandler(security_handler)
    
    # Configurar nivel de logging de la aplicación
    app.logger.setLevel(log_level)
    
    # Log de inicio de aplicación
    app.logger.info('Aplicación iniciada correctamente')

def register_error_handlers(app):
    """
    Registra los manejadores de errores personalizados
    
    Args:
        app: Instancia de la aplicación Flask
    """
    
    @app.errorhandler(400)
    def bad_request(error):
        """
        Maneja errores 400 (Bad Request)
        """
        # Log del error
        app.logger.warning(f'Error 400: {request.url} - IP: {get_client_ip(request)}')
        
        # Renderizar página de error personalizada
        return render_template('errors/400.html', 
                             error=error,
                             title='Solicitud Incorrecta'), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        """
        Maneja errores 401 (Unauthorized)
        """
        # Log del error de seguridad
        app.logger.warning(f'Error 401: Acceso no autorizado - {request.url} - IP: {get_client_ip(request)}')
        
        # Renderizar página de error personalizada
        return render_template('errors/401.html', 
                             error=error,
                             title='Acceso No Autorizado'), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        """
        Maneja errores 403 (Forbidden)
        """
        # Log del error de seguridad
        app.logger.warning(f'Error 403: Acceso prohibido - {request.url} - IP: {get_client_ip(request)}')
        
        # Renderizar página de error personalizada
        return render_template('errors/403.html', 
                             error=error,
                             title='Acceso Prohibido'), 403
    
    @app.errorhandler(404)
    def not_found(error):
        """
        Maneja errores 404 (Not Found)
        """
        # Log del error
        app.logger.warning(f'Error 404: Página no encontrada - {request.url} - IP: {get_client_ip(request)}')
        
        # Renderizar página de error personalizada
        return render_template('errors/404.html', 
                             error=error,
                             title='Página No Encontrada'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """
        Maneja errores 500 (Internal Server Error)
        """
        # Log del error crítico
        app.logger.error(f'Error 500: Error interno del servidor - {request.url} - IP: {get_client_ip(request)} - Error: {str(error)}')
        
        # Renderizar página de error personalizada
        return render_template('errors/500.html', 
                             error=error,
                             title='Error Interno del Servidor'), 500
    
    @app.errorhandler(503)
    def service_unavailable(error):
        """
        Maneja errores 503 (Service Unavailable)
        """
        # Log del error
        app.logger.error(f'Error 503: Servicio no disponible - {request.url} - IP: {get_client_ip(request)}')
        
        # Renderizar página de error personalizada
        return render_template('errors/503.html', 
                             error=error,
                             title='Servicio No Disponible'), 503

def log_user_activity(user_id, activity, details="", ip_address=None):
    """
    Registra actividad del usuario en el log de seguridad
    
    Args:
        user_id (int): ID del usuario
        activity (str): Tipo de actividad
        details (str): Detalles adicionales
        ip_address (str): Dirección IP del usuario
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Crear mensaje de log
    log_message = f"[{timestamp}] Usuario {user_id}: {activity}"
    if details:
        log_message += f" - {details}"
    if ip_address:
        log_message += f" - IP: {ip_address}"
    
    # Escribir en log de seguridad
    with open('logs/security.log', 'a', encoding='utf-8') as f:
        f.write(log_message + '\n')
    
    # También imprimir en consola para desarrollo
    if current_app.config['DEBUG']:
        print(f"ACTIVIDAD: {log_message}")

def log_security_event(event_type, details, ip_address=None, user_id=None):
    """
    Registra eventos de seguridad importantes
    
    Args:
        event_type (str): Tipo de evento de seguridad
        details (str): Detalles del evento
        ip_address (str): Dirección IP
        user_id (int): ID del usuario (opcional)
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Crear mensaje de log de seguridad
    log_message = f"[{timestamp}] SEGURIDAD - {event_type}: {details}"
    if ip_address:
        log_message += f" - IP: {ip_address}"
    if user_id:
        log_message += f" - Usuario: {user_id}"
    
    # Escribir en log de seguridad
    with open('logs/security.log', 'a', encoding='utf-8') as f:
        f.write(log_message + '\n')
    
    # También log en el logger de la aplicación
    current_app.logger.warning(log_message)

def log_database_error(operation, error, user_id=None):
    """
    Registra errores de base de datos
    
    Args:
        operation (str): Operación que falló
        error (str): Error específico
        user_id (int): ID del usuario (opcional)
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Crear mensaje de log
    log_message = f"[{timestamp}] ERROR BD - {operation}: {str(error)}"
    if user_id:
        log_message += f" - Usuario: {user_id}"
    
    # Escribir en log de errores
    with open('logs/error.log', 'a', encoding='utf-8') as f:
        f.write(log_message + '\n')
    
    # También log en el logger de la aplicación
    current_app.logger.error(log_message)

def cleanup_old_logs(days=30):
    """
    Limpia logs antiguos para evitar que ocupen mucho espacio
    
    Args:
        days (int): Días de antigüedad para considerar logs como antiguos
    """
    try:
        import glob
        from datetime import datetime, timedelta
        
        # Calcular fecha límite
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Buscar archivos de log antiguos
        log_files = glob.glob('logs/*.log.*')  # Logs rotados
        
        for log_file in log_files:
            # Obtener fecha de modificación del archivo
            file_time = datetime.fromtimestamp(os.path.getmtime(log_file))
            
            # Si el archivo es más antiguo que la fecha límite, eliminarlo
            if file_time < cutoff_date:
                os.remove(log_file)
                current_app.logger.info(f'Log antiguo eliminado: {log_file}')
    
    except Exception as e:
        current_app.logger.error(f'Error limpiando logs antiguos: {str(e)}')
