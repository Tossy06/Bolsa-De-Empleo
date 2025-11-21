# complaints/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinLengthValidator
from django.utils.crypto import get_random_string


class Complaint(models.Model):
    """
    Modelo para gestionar denuncias sobre incumplimiento de normas de inclusión
    """
    
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('under_review', 'En Revisión'),
        ('resolved', 'Resuelta'),
        ('rejected', 'Rechazada'),
    ]
    
    COMPLAINT_TYPE_CHOICES = [
        ('job_offer', 'Oferta de Empleo Discriminatoria'),
        ('recruitment_process', 'Proceso de Reclutamiento No Inclusivo'),
        ('workplace_accessibility', 'Falta de Accesibilidad en el Lugar de Trabajo'),
        ('discrimination', 'Discriminación o Acoso'),
        ('lack_of_adjustments', 'Negación de Ajustes Razonables'),
        ('quota_non_compliance', 'Incumplimiento de Cuotas de Empleo'),
        ('other', 'Otro'),
    ]
    
    # Identificador único público (para seguimiento)
    tracking_code = models.CharField(
        max_length=12,
        unique=True,
        editable=False,
        verbose_name='Código de seguimiento'
    )
    
    # Información de la denuncia
    complaint_type = models.CharField(
        max_length=50,
        choices=COMPLAINT_TYPE_CHOICES,
        verbose_name='Tipo de denuncia'
    )
    
    subject = models.CharField(
        max_length=200,
        verbose_name='Asunto',
        validators=[MinLengthValidator(10, 'El asunto debe tener al menos 10 caracteres')]
    )
    
    description = models.TextField(
        verbose_name='Descripción detallada',
        validators=[MinLengthValidator(50, 'La descripción debe tener al menos 50 caracteres')],
        help_text='Describa los hechos de manera detallada'
    )
    
    # Información sobre el denunciado (empresa u oferta)
    company_name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Nombre de la empresa'
    )
    
    job_posting_url = models.URLField(
        blank=True,
        verbose_name='URL de la oferta (opcional)'
    )
    
    # Información del denunciante (opcional y protegida)
    is_anonymous = models.BooleanField(
        default=True,
        verbose_name='Denuncia anónima'
    )
    
    complainant_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='filed_complaints',
        verbose_name='Usuario denunciante'
    )
    
    # Datos sensibles del denunciante (si proporciona)
    complainant_name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Nombre del denunciante (opcional)'
    )
    
    complainant_email = models.EmailField(
        blank=True,
        verbose_name='Email del denunciante (opcional)'
    )
    
    complainant_phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Teléfono del denunciante (opcional)'
    )
    
    # Archivos adjuntos (evidencia)
    evidence_file1 = models.FileField(
        upload_to='complaints/evidence/%Y/%m/',
        blank=True,
        null=True,
        verbose_name='Evidencia 1 (opcional)',
        help_text='Capturas de pantalla, documentos, etc.'
    )
    
    evidence_file2 = models.FileField(
        upload_to='complaints/evidence/%Y/%m/',
        blank=True,
        null=True,
        verbose_name='Evidencia 2 (opcional)'
    )
    
    evidence_file3 = models.FileField(
        upload_to='complaints/evidence/%Y/%m/',
        blank=True,
        null=True,
        verbose_name='Evidencia 3 (opcional)'
    )
    
    # Estado y seguimiento
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Estado'
    )
    
    priority = models.IntegerField(
        default=2,
        choices=[
            (1, 'Baja'),
            (2, 'Media'),
            (3, 'Alta'),
            (4, 'Urgente'),
        ],
        verbose_name='Prioridad'
    )
    
    # Respuesta del administrador
    admin_response = models.TextField(
        blank=True,
        verbose_name='Respuesta del administrador'
    )
    
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_complaints',
        verbose_name='Asignado a'
    )
    
    # Auditoría
    ip_address = models.GenericIPAddressField(
        blank=True,
        null=True,
        verbose_name='Dirección IP'
    )
    
    user_agent = models.TextField(
        blank=True,
        verbose_name='User Agent'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Última actualización')
    resolved_at = models.DateTimeField(blank=True, null=True, verbose_name='Fecha de resolución')
    
    class Meta:
        verbose_name = 'Denuncia'
        verbose_name_plural = 'Denuncias'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tracking_code']),
            models.Index(fields=['status', '-created_at']),
        ]
    
    def __str__(self):
        return f"Denuncia #{self.tracking_code} - {self.get_complaint_type_display()}"
    
    def save(self, *args, **kwargs):
        # Generar código de seguimiento único
        if not self.tracking_code:
            self.tracking_code = self.generate_tracking_code()
        
        # Actualizar fecha de resolución
        if self.status in ['resolved', 'rejected'] and not self.resolved_at:
            self.resolved_at = timezone.now()
        
        super().save(*args, **kwargs)
    
    @staticmethod
    def generate_tracking_code():
        """Genera un código de seguimiento único de 12 caracteres"""
        while True:
            code = get_random_string(12, allowed_chars='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
            if not Complaint.objects.filter(tracking_code=code).exists():
                return code
    
    def get_complainant_display_name(self):
        """Obtiene el nombre del denunciante o 'Anónimo'"""
        if self.is_anonymous or not self.complainant_name:
            return "Anónimo"
        return self.complainant_name
    
    def get_days_since_filed(self):
        """Retorna los días transcurridos desde la denuncia"""
        return (timezone.now() - self.created_at).days
    
    def get_status_badge_class(self):
        """Retorna la clase CSS para el badge de estado"""
        status_classes = {
            'pending': 'warning',
            'under_review': 'info',
            'resolved': 'success',
            'rejected': 'danger',
        }
        return status_classes.get(self.status, 'secondary')


class ComplaintComment(models.Model):
    """
    Comentarios internos sobre las denuncias (solo para administradores)
    """
    complaint = models.ForeignKey(
        Complaint,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Denuncia'
    )
    
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Autor'
    )
    
    comment = models.TextField(
        verbose_name='Comentario',
        validators=[MinLengthValidator(10, 'El comentario debe tener al menos 10 caracteres')]
    )
    
    is_internal = models.BooleanField(
        default=True,
        verbose_name='Comentario interno',
        help_text='Solo visible para administradores'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Comentario de Denuncia'
        verbose_name_plural = 'Comentarios de Denuncias'
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comentario de {self.author.get_full_name()} en {self.complaint.tracking_code}"


class ComplaintStatusHistory(models.Model):
    """
    Historial de cambios de estado de las denuncias
    """
    complaint = models.ForeignKey(
        Complaint,
        on_delete=models.CASCADE,
        related_name='status_history',
        verbose_name='Denuncia'
    )
    
    previous_status = models.CharField(
        max_length=20,
        choices=Complaint.STATUS_CHOICES,
        verbose_name='Estado anterior'
    )
    
    new_status = models.CharField(
        max_length=20,
        choices=Complaint.STATUS_CHOICES,
        verbose_name='Nuevo estado'
    )
    
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Cambiado por'
    )
    
    reason = models.TextField(
        blank=True,
        verbose_name='Razón del cambio'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Historial de Estado'
        verbose_name_plural = 'Historial de Estados'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.complaint.tracking_code}: {self.previous_status} → {self.new_status}"