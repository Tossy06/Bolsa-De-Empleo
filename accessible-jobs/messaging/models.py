# messaging/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import FileExtensionValidator


class Conversation(models.Model):
    """
    Conversación entre un candidato y una empresa
    """
    candidate = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='candidate_conversations',
        verbose_name='Candidato',
        limit_choices_to={'user_type': 'candidate'}
    )
    
    company = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='company_conversations',
        verbose_name='Empresa',
        limit_choices_to={'user_type': 'company'}
    )
    
    subject = models.CharField(
        max_length=200,
        verbose_name='Asunto'
    )
    
    # Referencia opcional a una oferta de trabajo (como texto)
    job_title = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Oferta de trabajo relacionada'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Última actualización')
    
    # Control de lectura
    candidate_last_read = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Última lectura del candidato'
    )
    
    company_last_read = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Última lectura de la empresa'
    )
    
    is_archived_by_candidate = models.BooleanField(
        default=False,
        verbose_name='Archivado por candidato'
    )
    
    is_archived_by_company = models.BooleanField(
        default=False,
        verbose_name='Archivado por empresa'
    )
    
    class Meta:
        verbose_name = 'Conversación'
        verbose_name_plural = 'Conversaciones'
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.subject} - {self.candidate.get_full_name()} & {self.company.get_full_name()}"
    
    def get_last_message(self):
        """Retorna el último mensaje de la conversación"""
        return self.messages.order_by('-created_at').first()
    
    def get_unread_count_for_candidate(self):
        """Retorna el número de mensajes no leídos por el candidato"""
        if not self.candidate_last_read:
            return self.messages.filter(sender=self.company).count()
        return self.messages.filter(
            sender=self.company,
            created_at__gt=self.candidate_last_read
        ).count()
    
    def get_unread_count_for_company(self):
        """Retorna el número de mensajes no leídos por la empresa"""
        if not self.company_last_read:
            return self.messages.filter(sender=self.candidate).count()
        return self.messages.filter(
            sender=self.candidate,
            created_at__gt=self.company_last_read
        ).count()
    
    def mark_as_read_by_user(self, user):
        """Marca la conversación como leída por un usuario"""
        if user == self.candidate:
            self.candidate_last_read = timezone.now()
        elif user == self.company:
            self.company_last_read = timezone.now()
        self.save(update_fields=['candidate_last_read', 'company_last_read'])
    
    def get_other_participant(self, user):
        """Retorna el otro participante de la conversación"""
        if user == self.candidate:
            return self.company
        return self.candidate


class Message(models.Model):
    """
    Mensaje individual dentro de una conversación
    """
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name='Conversación'
    )
    
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        verbose_name='Remitente'
    )
    
    content = models.TextField(
        verbose_name='Contenido del mensaje'
    )
    
    # Archivos adjuntos
    attachment = models.FileField(
        upload_to='messaging/attachments/%Y/%m/',
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(
                allowed_extensions=['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png', 'txt']
            )
        ],
        verbose_name='Archivo adjunto'
    )
    
    attachment_alt_text = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='Texto alternativo del archivo',
        help_text='Descripción accesible del archivo adjunto'
    )
    
    attachment_size = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='Tamaño del archivo (bytes)'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de envío')
    
    # Control de lectura
    is_read = models.BooleanField(
        default=False,
        verbose_name='Leído'
    )
    
    read_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de lectura'
    )
    
    class Meta:
        verbose_name = 'Mensaje'
        verbose_name_plural = 'Mensajes'
        ordering = ['created_at']
    
    def __str__(self):
        return f"Mensaje de {self.sender.get_full_name()} - {self.created_at}"
    
    def save(self, *args, **kwargs):
        # Calcular tamaño del archivo
        if self.attachment:
            self.attachment_size = self.attachment.size
        
        super().save(*args, **kwargs)
        
        # Actualizar timestamp de la conversación
        self.conversation.updated_at = timezone.now()
        self.conversation.save(update_fields=['updated_at'])
    
    def mark_as_read(self):
        """Marca el mensaje como leído"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])
    
    def get_recipient(self):
        """Retorna el receptor del mensaje"""
        if self.sender == self.conversation.candidate:
            return self.conversation.company
        return self.conversation.candidate
    
    def get_attachment_size_display(self):
        """Retorna el tamaño del archivo en formato legible"""
        if not self.attachment_size:
            return "N/A"
        
        size = self.attachment_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"


class MessageNotification(models.Model):
    """
    Notificaciones de nuevos mensajes
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='message_notifications',
        verbose_name='Usuario'
    )
    
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='notifications',
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
    
    class Meta:
        verbose_name = 'Notificación de Mensaje'
        verbose_name_plural = 'Notificaciones de Mensajes'
        ordering = ['-created_at']
        unique_together = ['user', 'message']
    
    def __str__(self):
        return f"Notificación para {self.user.get_full_name()} - Mensaje #{self.message.id}"