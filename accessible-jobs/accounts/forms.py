from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from django.contrib.auth.validators import UnicodeUsernameValidator
from hcaptcha.fields import hCaptchaField
from .models import User

class AccessibleUserCreationForm(UserCreationForm):
    """
    Formulario de registro accesible con hCaptcha
    Incluye atributos ARIA y labels descriptivos
    """
    
    # Campo hCaptcha accesible (tiene opción de audio)
    hcaptcha = hCaptchaField(
        label='Verificación de seguridad',
        help_text='Complete la verificación. Presione Tab para navegar al captcha y use las opciones de accesibilidad si lo necesita.'
    )
    
    # Checkbox para aceptar términos
    accept_terms = forms.BooleanField(
        required=True,
        label='Acepto los términos y condiciones',
        error_messages={
            'required': 'Debe aceptar los términos y condiciones para continuar'
        }
    )
    
    
    class Meta:
        model = User
        fields = ['user_type', 'username', 'email', 'first_name', 'last_name', 
                  'disability_type', 'password1', 'password2']
        
        # Widgets personalizados
        widgets = {
            'username': forms.TextInput(attrs={'autocomplete': 'username'}),
        }
        
        # Labels personalizados más descriptivos
        labels = {
            'username': 'Nombre de usuario',
            'email': 'Correo electrónico',
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'user_type': '¿Eres candidato o empresa?',
            'disability_type': 'Tipo de discapacidad (opcional)',
        }
        
        # Textos de ayuda accesibles
        help_texts = {
            'username': 'Identificador único para tu cuenta',
            'email': 'Usaremos este correo para comunicarnos contigo',
            'disability_type': 'Esta información es confidencial y nos ayuda a adaptar la plataforma a tus necesidades',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Remover el validador de username por defecto y permitir cualquier carácter
        self.fields['username'].validators = []
        
        # Añadir clases de Bootstrap y atributos ARIA a todos los campos
        for field_name, field in self.fields.items():
            # Clases de Bootstrap para estilo
            if field_name == 'accept_terms':
                field.widget.attrs['class'] = 'form-check-input'
            else:
                field.widget.attrs['class'] = 'form-control'
            
            # Atributos ARIA para accesibilidad
            field.widget.attrs['aria-label'] = field.label
            field.widget.attrs['aria-describedby'] = f'{field_name}_help'
            
            # Marcar campos requeridos visualmente y para lectores de pantalla
            if field.required:
                field.widget.attrs['aria-required'] = 'true'
        
        # Personalizar campos específicos
        self.fields['email'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        
        # Añadir atributo data para cambio dinámico de labels
        self.fields['user_type'].widget.attrs['id'] = 'id_user_type'
        self.fields['username'].widget.attrs['id'] = 'id_username'
        self.fields['first_name'].widget.attrs['id'] = 'id_first_name'
        self.fields['last_name'].widget.attrs['id'] = 'id_last_name'
        
        # Mejorar el campo de contraseña con instrucciones claras
        self.fields['password1'].help_text = (
            'Tu contraseña debe contener al menos 8 caracteres, '
            'no puede ser completamente numérica y no debe ser muy común.'
        )
        
        self.fields['password2'].help_text = (
            'Ingresa la misma contraseña nuevamente para verificación.'
        )
    
    def clean_email(self):
        """Valida que el email no esté ya registrado"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError(
                'Este correo electrónico ya está registrado. '
                'Por favor usa otro o intenta iniciar sesión.'
            )
        return email
    
    def clean_username(self):
        """Valida que el nombre de usuario no esté ya registrado"""
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError(
                'Este nombre de usuario ya está en uso. '
                'Por favor elige otro.'
            )
        return username


class AccessibleLoginForm(AuthenticationForm):
    """
    Formulario de login accesible
    Simplificado con buenas prácticas de accesibilidad
    """
    
    # Checkbox de "recordarme"
    remember_me = forms.BooleanField(
        required=False,
        initial=False,
        label='Mantener sesión iniciada',
        help_text='Marca esta casilla si estás en un dispositivo personal'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Personalizar campos con Bootstrap y ARIA
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Nombre de usuario',
            'aria-label': 'Nombre de usuario',
            'aria-describedby': 'username_help',
            'autofocus': True,
        })
        
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Contraseña',
            'aria-label': 'Contraseña',
            'aria-describedby': 'password_help',
        })
        
        self.fields['remember_me'].widget.attrs.update({
            'class': 'form-check-input',
            'aria-label': 'Mantener sesión iniciada',
        })
        
        # Labels más amigables
        self.fields['username'].label = 'Usuario o correo'
        self.fields['password'].label = 'Contraseña'