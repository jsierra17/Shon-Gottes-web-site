"""
Sistema de recuperación de contraseña
Incluye generación de tokens, envío de emails y validación
"""
import sqlite3
import os
from datetime import datetime, timedelta
from flask import current_app
from flask_mail import Message
from utils import generate_reset_token, log_security_event, log_database_error

class PasswordResetManager:
    """
    Gestor de recuperación de contraseñas
    Maneja tokens, emails y validaciones
    """
    
    def __init__(self, mail):
        """
        Inicializa el gestor de recuperación de contraseñas
        
        Args:
            mail: Instancia de Flask-Mail
        """
        self.mail = mail
        self.db_name = "database.db"
        self.token_expiry_hours = 24  # Token válido por 24 horas
    
    def create_reset_table(self):
        """
        Crea la tabla para tokens de recuperación de contraseña
        """
        try:
            with sqlite3.connect(self.db_name) as conexion:
                cursor = conexion.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS password_reset_tokens (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        token TEXT UNIQUE NOT NULL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        expires_at DATETIME NOT NULL,
                        used BOOLEAN DEFAULT FALSE,
                        FOREIGN KEY (user_id) REFERENCES usuarios(id)
                    )
                """)
                conexion.commit()
                current_app.logger.info("Tabla de tokens de recuperación creada correctamente")
        except Exception as e:
            log_database_error("crear_tabla_reset", str(e))
            raise
    
    def request_password_reset(self, email, ip_address=None):
        """
        Solicita un reset de contraseña para un email
        
        Args:
            email (str): Email del usuario
            ip_address (str): IP del usuario que solicita el reset
            
        Returns:
            tuple: (success, message)
        """
        try:
            # Verificar si el email existe en la base de datos
            with sqlite3.connect(self.db_name) as conexion:
                cursor = conexion.cursor()
                cursor.execute("SELECT id, nombre FROM usuarios WHERE correo = ?", (email,))
                user = cursor.fetchone()
                
                if not user:
                    # Por seguridad, no revelamos si el email existe o no
                    return True, "Si el email existe, recibirás un enlace de recuperación"
                
                user_id, user_name = user
                
                # Generar token único
                token = generate_reset_token()
                
                # Calcular fecha de expiración
                expires_at = datetime.now() + timedelta(hours=self.token_expiry_hours)
                
                # Invalidar tokens anteriores del usuario
                cursor.execute("""
                    UPDATE password_reset_tokens 
                    SET used = TRUE 
                    WHERE user_id = ? AND used = FALSE
                """, (user_id,))
                
                # Insertar nuevo token
                cursor.execute("""
                    INSERT INTO password_reset_tokens (user_id, token, expires_at)
                    VALUES (?, ?, ?)
                """, (user_id, token, expires_at))
                
                conexion.commit()
                
                # Enviar email de recuperación
                success = self._send_reset_email(email, user_name, token)
                
                if success:
                    # Log de actividad de seguridad
                    log_security_event(
                        "PASSWORD_RESET_REQUESTED",
                        f"Usuario {user_id} solicitó reset de contraseña",
                        ip_address,
                        user_id
                    )
                    return True, "Si el email existe, recibirás un enlace de recuperación"
                else:
                    return False, "Error enviando el email de recuperación"
                    
        except Exception as e:
            log_database_error("solicitar_reset_password", str(e))
            return False, "Error procesando la solicitud"
    
    def _send_reset_email(self, email, user_name, token):
        """
        Envía el email de recuperación de contraseña
        
        Args:
            email (str): Email del usuario
            user_name (str): Nombre del usuario
            token (str): Token de recuperación
            
        Returns:
            bool: True si se envió correctamente
        """
        try:
            # Crear URL de reset
            reset_url = f"{current_app.config.get('BASE_URL', 'http://localhost:5000')}/reset-password/{token}"
            
            # Crear mensaje de email
            msg = Message(
                subject='Recuperación de Contraseña - Shon Gottes Web Site',
                recipients=[email],
                sender=current_app.config['MAIL_DEFAULT_SENDER']
            )
            
            # Contenido del email
            msg.html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: #2ecc71; color: white; padding: 20px; text-align: center; }}
                    .content {{ padding: 20px; background: #f9f9f9; }}
                    .button {{ display: inline-block; background: #2ecc71; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                    .footer {{ padding: 20px; text-align: center; color: #666; font-size: 12px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Recuperación de Contraseña</h1>
                    </div>
                    <div class="content">
                        <h2>Hola {user_name},</h2>
                        <p>Recibimos una solicitud para restablecer la contraseña de tu cuenta en Shon Gottes Web Site.</p>
                        <p>Si solicitaste este cambio, haz clic en el botón de abajo para crear una nueva contraseña:</p>
                        <a href="{reset_url}" class="button">Restablecer Contraseña</a>
                        <p>Este enlace expirará en {self.token_expiry_hours} horas.</p>
                        <p>Si no solicitaste este cambio, puedes ignorar este email. Tu contraseña no será modificada.</p>
                    </div>
                    <div class="footer">
                        <p>Este es un email automático, por favor no respondas.</p>
                        <p>© 2025 Shon Gottes Web Site - Jose Sierra</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Enviar email
            self.mail.send(msg)
            current_app.logger.info(f"Email de recuperación enviado a {email}")
            return True
            
        except Exception as e:
            current_app.logger.error(f"Error enviando email de recuperación: {str(e)}")
            return False
    
    def validate_reset_token(self, token):
        """
        Valida si un token de recuperación es válido
        
        Args:
            token (str): Token a validar
            
        Returns:
            tuple: (is_valid, user_id, message)
        """
        try:
            with sqlite3.connect(self.db_name) as conexion:
                cursor = conexion.cursor()
                cursor.execute("""
                    SELECT user_id, expires_at, used 
                    FROM password_reset_tokens 
                    WHERE token = ?
                """, (token,))
                
                result = cursor.fetchone()
                
                if not result:
                    return False, None, "Token inválido"
                
                user_id, expires_at, used = result
                
                # Verificar si el token ya fue usado
                if used:
                    return False, None, "Este enlace ya fue utilizado"
                
                # Verificar si el token expiró
                if datetime.now() > datetime.fromisoformat(expires_at):
                    return False, None, "Este enlace ha expirado"
                
                return True, user_id, "Token válido"
                
        except Exception as e:
            log_database_error("validar_token_reset", str(e))
            return False, None, "Error validando el token"
    
    def reset_password(self, token, new_password, ip_address=None):
        """
        Restablece la contraseña usando un token válido
        
        Args:
            token (str): Token de recuperación
            new_password (str): Nueva contraseña
            ip_address (str): IP del usuario
            
        Returns:
            tuple: (success, message)
        """
        try:
            # Validar token
            is_valid, user_id, message = self.validate_reset_token(token)
            
            if not is_valid:
                return False, message
            
            # Hash de la nueva contraseña
            from utils import hash_password
            password_hash = hash_password(new_password)
            
            # Actualizar contraseña en la base de datos
            with sqlite3.connect(self.db_name) as conexion:
                cursor = conexion.cursor()
                cursor.execute("""
                    UPDATE usuarios 
                    SET contraseña = ? 
                    WHERE id = ?
                """, (password_hash, user_id))
                
                # Marcar token como usado
                cursor.execute("""
                    UPDATE password_reset_tokens 
                    SET used = TRUE 
                    WHERE token = ?
                """, (token,))
                
                conexion.commit()
                
                # Log de actividad de seguridad
                log_security_event(
                    "PASSWORD_RESET_COMPLETED",
                    f"Usuario {user_id} restableció su contraseña",
                    ip_address,
                    user_id
                )
                
                return True, "Contraseña restablecida correctamente"
                
        except Exception as e:
            log_database_error("reset_password", str(e))
            return False, "Error restableciendo la contraseña"
    
    def cleanup_expired_tokens(self):
        """
        Limpia tokens expirados de la base de datos
        """
        try:
            with sqlite3.connect(self.db_name) as conexion:
                cursor = conexion.cursor()
                cursor.execute("""
                    DELETE FROM password_reset_tokens 
                    WHERE expires_at < ? OR used = TRUE
                """, (datetime.now(),))
                
                deleted_count = cursor.rowcount
                conexion.commit()
                
                if deleted_count > 0:
                    current_app.logger.info(f"Se eliminaron {deleted_count} tokens expirados")
                    
        except Exception as e:
            log_database_error("limpiar_tokens_expirados", str(e))
