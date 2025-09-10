"""
Formularios seguros usando Flask-WTF
Incluye validaciones y protección CSRF
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from utils import validate_email_address, validate_password_strength, is_valid_name

class RegistrationForm(FlaskForm):
    """
    Formulario de registro de usuarios
    Incluye validaciones personalizadas y protección CSRF
    """
    
    # Campo de nombre con validaciones
    nombre = StringField(
        'Nombre Completo',
        validators=[
            DataRequired(message='El nombre es obligatorio'),  # Campo requerido
            Length(min=2, max=50, message='El nombre debe tener entre 2 y 50 caracteres')  # Longitud válida
        ],
        render_kw={
            'placeholder': 'Ingresa tu nombre completo',
            'class': 'form-control',
            'maxlength': '50'
        }
    )
    
    # Campo de email con validaciones
    correo = StringField(
        'Correo Electrónico',
        validators=[
            DataRequired(message='El correo es obligatorio'),  # Campo requerido
            Email(message='Formato de email inválido'),  # Formato de email válido
            Length(max=100, message='El correo no puede tener más de 100 caracteres')  # Longitud máxima
        ],
        render_kw={
            'placeholder': 'ejemplo@correo.com',
            'class': 'form-control',
            'type': 'email',
            'maxlength': '100'
        }
    )
    
    # Campo de contraseña con validaciones
    contraseña = PasswordField(
        'Contraseña',
        validators=[
            DataRequired(message='La contraseña es obligatoria'),  # Campo requerido
            Length(min=8, max=128, message='La contraseña debe tener entre 8 y 128 caracteres')  # Longitud válida
        ],
        render_kw={
            'placeholder': 'Mínimo 8 caracteres',
            'class': 'form-control',
            'minlength': '8',
            'maxlength': '128'
        }
    )
    
    # Campo de confirmación de contraseña
    confirmar_contraseña = PasswordField(
        'Confirmar Contraseña',
        validators=[
            DataRequired(message='Debes confirmar la contraseña'),  # Campo requerido
            EqualTo('contraseña', message='Las contraseñas no coinciden')  # Debe coincidir con contraseña
        ],
        render_kw={
            'placeholder': 'Repite tu contraseña',
            'class': 'form-control',
            'minlength': '8',
            'maxlength': '128'
        }
    )
    
    # Botón de envío
    submit = SubmitField(
        'Registrarse',
        render_kw={
            'class': 'btn btn-brand w-100 py-2'
        }
    )
    
    def validate_nombre(self, field):
        """
        Validación personalizada para el nombre
        Verifica que el nombre sea válido usando la función de utils
        """
        is_valid, message = is_valid_name(field.data)
        if not is_valid:
            raise ValidationError(message)
    
    def validate_correo(self, field):
        """
        Validación personalizada para el email
        Verifica que el email sea válido y no esté en uso
        """
        is_valid, message = validate_email_address(field.data)
        if not is_valid:
            raise ValidationError(message)
    
    def validate_contraseña(self, field):
        """
        Validación personalizada para la contraseña
        Verifica que la contraseña cumpla con los requisitos de seguridad
        """
        is_valid, message = validate_password_strength(field.data)
        if not is_valid:
            raise ValidationError(message)

class LoginForm(FlaskForm):
    """
    Formulario de inicio de sesión
    Incluye validaciones básicas y protección CSRF
    """
    
    # Campo de email
    correo = StringField(
        'Correo Electrónico',
        validators=[
            DataRequired(message='El correo es obligatorio'),  # Campo requerido
            Email(message='Formato de email inválido')  # Formato de email válido
        ],
        render_kw={
            'placeholder': 'ejemplo@correo.com',
            'class': 'form-control',
            'type': 'email'
        }
    )
    
    # Campo de contraseña
    contraseña = PasswordField(
        'Contraseña',
        validators=[
            DataRequired(message='La contraseña es obligatoria')  # Campo requerido
        ],
        render_kw={
            'placeholder': 'Tu contraseña',
            'class': 'form-control'
        }
    )
    
    # Botón de envío
    submit = SubmitField(
        'Iniciar Sesión',
        render_kw={
            'class': 'btn btn-brand w-100 py-2'
        }
    )

class PasswordResetForm(FlaskForm):
    """
    Formulario para solicitar recuperación de contraseña
    """
    
    # Campo de email
    correo = StringField(
        'Correo Electrónico',
        validators=[
            DataRequired(message='El correo es obligatorio'),  # Campo requerido
            Email(message='Formato de email inválido')  # Formato de email válido
        ],
        render_kw={
            'placeholder': 'ejemplo@correo.com',
            'class': 'form-control',
            'type': 'email'
        }
    )
    
    # Botón de envío
    submit = SubmitField(
        'Enviar Enlace de Recuperación',
        render_kw={
            'class': 'btn btn-brand w-100 py-2'
        }
    )

class NewPasswordForm(FlaskForm):
    """
    Formulario para establecer nueva contraseña
    """
    
    # Campo de nueva contraseña
    nueva_contraseña = PasswordField(
        'Nueva Contraseña',
        validators=[
            DataRequired(message='La contraseña es obligatoria'),  # Campo requerido
            Length(min=8, max=128, message='La contraseña debe tener entre 8 y 128 caracteres')  # Longitud válida
        ],
        render_kw={
            'placeholder': 'Mínimo 8 caracteres',
            'class': 'form-control',
            'minlength': '8',
            'maxlength': '128'
        }
    )
    
    # Campo de confirmación de nueva contraseña
    confirmar_contraseña = PasswordField(
        'Confirmar Nueva Contraseña',
        validators=[
            DataRequired(message='Debes confirmar la contraseña'),  # Campo requerido
            EqualTo('nueva_contraseña', message='Las contraseñas no coinciden')  # Debe coincidir
        ],
        render_kw={
            'placeholder': 'Repite tu nueva contraseña',
            'class': 'form-control',
            'minlength': '8',
            'maxlength': '128'
        }
    )
    
    # Botón de envío
    submit = SubmitField(
        'Cambiar Contraseña',
        render_kw={
            'class': 'btn btn-brand w-100 py-2'
        }
    )
    
    def validate_nueva_contraseña(self, field):
        """
        Validación personalizada para la nueva contraseña
        Verifica que la contraseña cumpla con los requisitos de seguridad
        """
        is_valid, message = validate_password_strength(field.data)
        if not is_valid:
            raise ValidationError(message)

class ContactForm(FlaskForm):
    """
    Formulario de contacto
    """
    
    # Campo de nombre
    nombre = StringField(
        'Nombre',
        validators=[
            DataRequired(message='El nombre es obligatorio'),  # Campo requerido
            Length(min=2, max=50, message='El nombre debe tener entre 2 y 50 caracteres')  # Longitud válida
        ],
        render_kw={
            'placeholder': 'Tu nombre',
            'class': 'form-control',
            'maxlength': '50'
        }
    )
    
    # Campo de email
    correo = StringField(
        'Correo Electrónico',
        validators=[
            DataRequired(message='El correo es obligatorio'),  # Campo requerido
            Email(message='Formato de email inválido')  # Formato de email válido
        ],
        render_kw={
            'placeholder': 'ejemplo@correo.com',
            'class': 'form-control',
            'type': 'email'
        }
    )
    
    # Campo de asunto
    asunto = SelectField(
        'Asunto',
        choices=[
            ('', 'Selecciona un asunto'),
            ('consulta', 'Consulta general'),
            ('proyecto', 'Propuesta de proyecto'),
            ('colaboracion', 'Colaboración'),
            ('otro', 'Otro')
        ],
        validators=[
            DataRequired(message='Debes seleccionar un asunto')  # Campo requerido
        ],
        render_kw={
            'class': 'form-control'
        }
    )
    
    # Campo de mensaje
    mensaje = TextAreaField(
        'Mensaje',
        validators=[
            DataRequired(message='El mensaje es obligatorio'),  # Campo requerido
            Length(min=10, max=1000, message='El mensaje debe tener entre 10 y 1000 caracteres')  # Longitud válida
        ],
        render_kw={
            'placeholder': 'Escribe tu mensaje aquí...',
            'class': 'form-control',
            'rows': '5',
            'maxlength': '1000'
        }
    )
    
    # Botón de envío
    submit = SubmitField(
        'Enviar Mensaje',
        render_kw={
            'class': 'btn btn-brand w-100 py-2'
        }
    )
