from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    """
    Modelo de usuario personalizado
    """
    
    # Tipos de usuario
    USER_TYPE_CHOICES = [
        ('candidate', 'Candidato'),
        ('company', 'Empresa'),
        ('admin', 'Administrador'),
    ]
    
    # Tipos de discapacidad (para estadísticas y adaptaciones)
    DISABILITY_CHOICES = [
        ('none', 'Sin discapacidad'),
        ('visual', 'Visual'),
        ('auditive', 'Auditiva'),
        ('motor', 'Motriz'),
        ('cognitive', 'Cognitiva'),
        ('multiple', 'Múltiple'),
        ('other', 'Otra'),
        ('prefer_not_say', 'Prefiero no decirlo'),
    ]
    
    # Campos adicionales
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default='candidate',
        verbose_name='Tipo de usuario',
        help_text='Define si el usuario es un candidato o una empresa'
    )
    
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Teléfono',
        help_text='Número de contacto del usuario'
    )
    
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        blank=True,
        null=True,
        verbose_name='Foto de perfil',
        help_text='Imagen de perfil del usuario (opcional)'
    )
    
    # Campos de accesibilidad
    disability_type = models.CharField(
        max_length=20,
        choices=DISABILITY_CHOICES,
        default='prefer_not_say',
        verbose_name='Tipo de discapacidad',
        help_text='Esta información es confidencial y nos ayuda a mejorar la accesibilidad'
    )
    
    requires_screen_reader = models.BooleanField(
        default=False,
        verbose_name='Usa lector de pantalla',
        help_text='Indica si el usuario utiliza tecnología de lectura de pantalla'
    )
    
    high_contrast_mode = models.BooleanField(
        default=False,
        verbose_name='Modo alto contraste',
        help_text='Activa un tema con mayor contraste para facilitar la lectura'
    )
    
    large_text_mode = models.BooleanField(
        default=False,
        verbose_name='Texto grande',
        help_text='Aumenta el tamaño de la fuente en toda la plataforma'
    )
    
    # Campos de auditoría
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de registro'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Última actualización'
    )
    
    email_verified = models.BooleanField(
        default=False,
        verbose_name='Email verificado',
        help_text='Indica si el usuario ha verificado su correo electrónico'
    )
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"
    
    def get_full_name(self):
        """Retorna el nombre completo del usuario"""
        return f"{self.first_name} {self.last_name}".strip() or self.username