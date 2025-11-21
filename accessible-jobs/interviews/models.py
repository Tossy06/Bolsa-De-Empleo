# interviews/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import URLValidator
import uuid
from datetime import datetime


class Interview(models.Model):
    """
    Entrevista programada entre empresa y candidato
    """
    
    STATUS_CHOICES = [
        ('proposed', 'Propuesta'),
        ('confirmed', 'Confirmada'),
        ('cancelled', 'Cancelada'),
        ('completed', 'Completada'),
        ('rescheduled', 'Reprogramada'),
    ]
    
    INTERVIEW_TYPE_CHOICES = [
        ('in_person', 'Presencial'),
        ('online', 'En línea'),
        ('phone', 'Telefónica'),
        ('hybrid', 'Híbrida'),
    ]
    
    PLATFORM_CHOICES = [
        ('zoom', 'Zoom'),
        ('teams', 'Microsoft Teams'),
        ('meet', 'Google Meet'),
        ('webex', 'Cisco Webex'),
        ('other', 'Otra plataforma'),
    ]
    
    # IDs
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    # Participantes
    company = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='company_interviews',
        verbose_name='Empresa',
        limit_choices_to={'user_type': 'company'}
    )
    
    candidate = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='candidate_interviews',
        verbose_name='Candidato',
        limit_choices_to={'user_type': 'candidate'}
    )
    
    # Referencia a oferta de trabajo (opcional, como texto)
    job_title = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Título del puesto'
    )
    
    # Detalles de la entrevista
    title = models.CharField(
        max_length=200,
        verbose_name='Título de la entrevista',
        help_text='Ej: Entrevista técnica - Desarrollador Frontend'
    )
    
    description = models.TextField(
        verbose_name='Descripción',
        help_text='Detalles sobre la entrevista, temas a tratar, etc.'
    )
    
    # Fecha y hora
    scheduled_date = models.DateField(
        verbose_name='Fecha programada'
    )
    
    scheduled_time = models.TimeField(
        verbose_name='Hora programada'
    )
    
    duration_minutes = models.PositiveIntegerField(
        default=60,
        verbose_name='Duración (minutos)',
        help_text='Duración estimada de la entrevista'
    )
    
    # Tipo y plataforma
    interview_type = models.CharField(
        max_length=20,
        choices=INTERVIEW_TYPE_CHOICES,
        default='online',
        verbose_name='Tipo de entrevista'
    )
    
    platform = models.CharField(
        max_length=20,
        choices=PLATFORM_CHOICES,
        blank=True,
        verbose_name='Plataforma de reunión',
        help_text='Solo para entrevistas en línea'
    )
    
    meeting_url = models.URLField(
        blank=True,
        verbose_name='URL de la reunión',
        validators=[URLValidator()],
        help_text='Link de Zoom, Teams, Meet, etc.'
    )
    
    meeting_id = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='ID de la reunión'
    )
    
    meeting_password = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Contraseña de la reunión'
    )
    
    # Ubicación física (para entrevistas presenciales)
    location_address = models.TextField(
        blank=True,
        verbose_name='Dirección',
        help_text='Dirección completa para entrevistas presenciales'
    )
    
    location_instructions = models.TextField(
        blank=True,
        verbose_name='Instrucciones de ubicación',
        help_text='Cómo llegar, piso, oficina, etc.'
    )
    
    # ✨ OPCIONES DE ACCESIBILIDAD
    requires_sign_language_interpreter = models.BooleanField(
        default=False,
        verbose_name='Requiere intérprete de lengua de señas'
    )
    
    requires_accessible_location = models.BooleanField(
        default=False,
        verbose_name='Requiere ubicación accesible (rampa, ascensor)'
    )
    
    requires_screen_reader_support = models.BooleanField(
        default=False,
        verbose_name='Requiere soporte para lector de pantalla'
    )
    
    requires_captioning = models.BooleanField(
        default=False,
        verbose_name='Requiere subtítulos en tiempo real'
    )
    
    other_accessibility_needs = models.TextField(
        blank=True,
        verbose_name='Otras necesidades de accesibilidad',
        help_text='Describa cualquier otra necesidad especial'
    )
    
    # Notas adicionales
    company_notes = models.TextField(
        blank=True,
        verbose_name='Notas de la empresa',
        help_text='Notas internas de la empresa sobre el candidato'
    )
    
    # Estado
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='proposed',
        verbose_name='Estado'
    )
    
    # Confirmaciones
    company_confirmed = models.BooleanField(
        default=True,
        verbose_name='Confirmado por empresa'
    )
    
    candidate_confirmed = models.BooleanField(
        default=False,
        verbose_name='Confirmado por candidato'
    )
    
    # Cancelación
    cancelled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cancelled_interviews',
        verbose_name='Cancelado por'
    )
    
    cancellation_reason = models.TextField(
        blank=True,
        verbose_name='Razón de cancelación'
    )
    
    # Feedback post-entrevista
    company_feedback = models.TextField(
        blank=True,
        verbose_name='Comentarios de la empresa'
    )
    
    candidate_feedback = models.TextField(
        blank=True,
        verbose_name='Comentarios del candidato'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Entrevista'
        verbose_name_plural = 'Entrevistas'
        ordering = ['-scheduled_date', '-scheduled_time']
        indexes = [
            models.Index(fields=['company', 'scheduled_date']),
            models.Index(fields=['candidate', 'scheduled_date']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.scheduled_date} {self.scheduled_time}"
    
    def get_datetime(self):
        """Retorna datetime combinado con timezone"""
        naive_datetime = datetime.combine(self.scheduled_date, self.scheduled_time)
        return timezone.make_aware(naive_datetime)
    
    def is_past(self):
        """Verifica si la entrevista ya pasó"""
        return self.get_datetime() < timezone.now()
    
    def is_upcoming(self):
        """Verifica si la entrevista es próxima"""
        return self.get_datetime() > timezone.now() and self.status in ['proposed', 'confirmed']
    
    def can_be_cancelled(self):
        """Verifica si la entrevista puede ser cancelada"""
        return self.status in ['proposed', 'confirmed'] and not self.is_past()
    
    def confirm_by_candidate(self):
        """Confirma la entrevista por parte del candidato"""
        if self.status == 'proposed':
            self.candidate_confirmed = True
            if self.company_confirmed:
                self.status = 'confirmed'
                self.confirmed_at = timezone.now()
            self.save()
    
    def cancel(self, user, reason=''):
        """Cancela la entrevista"""
        if self.can_be_cancelled():
            self.status = 'cancelled'
            self.cancelled_by = user
            self.cancellation_reason = reason
            self.cancelled_at = timezone.now()
            self.save()
    
    def mark_as_completed(self):
        """Marca la entrevista como completada"""
        if self.is_past() and self.status == 'confirmed':
            self.status = 'completed'
            self.completed_at = timezone.now()
            self.save()
    
    def get_accessibility_requirements_list(self):
        """Retorna lista de requisitos de accesibilidad"""
        requirements = []
        if self.requires_sign_language_interpreter:
            requirements.append('Intérprete de lengua de señas')
        if self.requires_accessible_location:
            requirements.append('Ubicación accesible')
        if self.requires_screen_reader_support:
            requirements.append('Soporte para lector de pantalla')
        if self.requires_captioning:
            requirements.append('Subtítulos en tiempo real')
        if self.other_accessibility_needs:
            requirements.append(self.other_accessibility_needs)
        return requirements
    
    def get_platform_display_with_icon(self):
        """Retorna el nombre de la plataforma con icono"""
        icons = {
            'zoom': '📹',
            'teams': '💼',
            'meet': '🎥',
            'webex': '📞',
            'other': '🌐',
        }
        return f"{icons.get(self.platform, '🌐')} {self.get_platform_display()}"


class InterviewRescheduleRequest(models.Model):
    """
    Solicitud de reprogramación de entrevista
    """
    interview = models.ForeignKey(
        Interview,
        on_delete=models.CASCADE,
        related_name='reschedule_requests',
        verbose_name='Entrevista'
    )
    
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reschedule_requests',
        verbose_name='Solicitado por'
    )
    
    reason = models.TextField(
        verbose_name='Razón de la reprogramación'
    )
    
    proposed_date = models.DateField(
        verbose_name='Nueva fecha propuesta'
    )
    
    proposed_time = models.TimeField(
        verbose_name='Nueva hora propuesta'
    )
    
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pendiente'),
            ('accepted', 'Aceptada'),
            ('rejected', 'Rechazada'),
        ],
        default='pending',
        verbose_name='Estado'
    )
    
    response = models.TextField(
        blank=True,
        verbose_name='Respuesta'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Solicitud de Reprogramación'
        verbose_name_plural = 'Solicitudes de Reprogramación'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Reprogramación de {self.interview.title} - {self.get_status_display()}"


class InterviewNotification(models.Model):
    """
    Notificaciones sobre entrevistas
    """
    NOTIFICATION_TYPES = [
        ('created', 'Entrevista creada'),
        ('confirmed', 'Entrevista confirmada'),
        ('cancelled', 'Entrevista cancelada'),
        ('rescheduled', 'Entrevista reprogramada'),
        ('reminder_24h', 'Recordatorio 24h antes'),
        ('reminder_1h', 'Recordatorio 1h antes'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='interview_notifications',
        verbose_name='Usuario'
    )
    
    interview = models.ForeignKey(
        Interview,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='Entrevista'
    )
    
    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPES,
        verbose_name='Tipo de notificación'
    )
    
    message = models.TextField(
        verbose_name='Mensaje'
    )
    
    is_read = models.BooleanField(
        default=False,
        verbose_name='Leída'
    )
    
    is_email_sent = models.BooleanField(
        default=False,
        verbose_name='Email enviado'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Notificación de Entrevista'
        verbose_name_plural = 'Notificaciones de Entrevistas'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_notification_type_display()} - {self.user.get_full_name()}"