# library/models.py
from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.core.validators import FileExtensionValidator


class ResourceCategory(models.Model):
    """
    Categorías para organizar los recursos de la biblioteca
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Nombre de la categoría'
    )
    
    slug = models.SlugField(
        max_length=120,
        unique=True,
        blank=True
    )
    
    description = models.TextField(
        blank=True,
        verbose_name='Descripción'
    )
    
    icon = models.CharField(
        max_length=50,
        default='bi-folder',
        verbose_name='Icono de Bootstrap',
        help_text='Clase de icono de Bootstrap Icons (ej: bi-folder, bi-people)'
    )
    
    order = models.PositiveIntegerField(
        default=0,
        verbose_name='Orden de visualización'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Categoría activa'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Categoría de Recurso'
        verbose_name_plural = 'Categorías de Recursos'
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_resources_count(self):
        """Retorna el número de recursos en esta categoría"""
        return self.resources.filter(is_published=True).count()


class BestPracticeResource(models.Model):
    """
    Recursos y documentos de mejores prácticas
    """
    
    RESOURCE_TYPE_CHOICES = [
        ('document', 'Documento (PDF)'),
        ('guide', 'Guía'),
        ('checklist', 'Lista de Verificación'),
        ('template', 'Plantilla'),
        ('case_study', 'Caso de Estudio'),
        ('article', 'Artículo'),
        ('video', 'Video'),
        ('infographic', 'Infografía'),
    ]
    
    title = models.CharField(
        max_length=250,
        verbose_name='Título del recurso'
    )
    
    slug = models.SlugField(
        max_length=300,
        unique=True,
        blank=True
    )
    
    category = models.ForeignKey(
        ResourceCategory,
        on_delete=models.CASCADE,
        related_name='resources',
        verbose_name='Categoría'
    )
    
    resource_type = models.CharField(
        max_length=20,
        choices=RESOURCE_TYPE_CHOICES,
        default='document',
        verbose_name='Tipo de recurso'
    )
    
    description = models.TextField(
        verbose_name='Descripción',
        help_text='Resumen del contenido del recurso'
    )
    
    content = models.TextField(
        blank=True,
        verbose_name='Contenido completo',
        help_text='Contenido textual del recurso (opcional si hay archivo adjunto)'
    )
    
    # Archivo adjunto
    file = models.FileField(
        upload_to='library/resources/%Y/%m/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx'])],
        verbose_name='Archivo adjunto',
        help_text='PDF, Word, Excel o PowerPoint'
    )
    
    file_size = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name='Tamaño del archivo (bytes)'
    )
    
    # URL externa (alternativa al archivo)
    external_url = models.URLField(
        blank=True,
        null=True,
        verbose_name='URL externa',
        help_text='Enlace a recurso externo (si no hay archivo adjunto)'
    )
    
    # Metadatos
    author = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Autor o fuente'
    )
    
    publication_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='Fecha de publicación'
    )
    
    tags = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='Etiquetas',
        help_text='Separadas por comas (ej: reclutamiento, accesibilidad, onboarding)'
    )
    
    # Control de publicación
    is_published = models.BooleanField(
        default=True,
        verbose_name='Publicado'
    )
    
    is_featured = models.BooleanField(
        default=False,
        verbose_name='Destacado',
        help_text='Aparecerá en la sección de recursos destacados'
    )
    
    # Accesibilidad
    is_accessible = models.BooleanField(
        default=True,
        verbose_name='Accesible (compatible con lectores de pantalla)'
    )
    
    accessibility_notes = models.TextField(
        blank=True,
        verbose_name='Notas de accesibilidad',
        help_text='Información adicional sobre características de accesibilidad'
    )
    
    # Estadísticas
    view_count = models.PositiveIntegerField(
        default=0,
        verbose_name='Número de vistas'
    )
    
    download_count = models.PositiveIntegerField(
        default=0,
        verbose_name='Número de descargas'
    )
    
    # Auditoría
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_resources',
        verbose_name='Creado por'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Recurso de Mejores Prácticas'
        verbose_name_plural = 'Recursos de Mejores Prácticas'
        ordering = ['-is_featured', '-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        
        # Calcular tamaño del archivo
        if self.file:
            self.file_size = self.file.size
        
        super().save(*args, **kwargs)
    
    def increment_view_count(self):
        """Incrementa el contador de vistas"""
        self.view_count += 1
        self.save(update_fields=['view_count'])
    
    def increment_download_count(self):
        """Incrementa el contador de descargas"""
        self.download_count += 1
        self.save(update_fields=['download_count'])
    
    def get_tags_list(self):
        """Retorna las etiquetas como lista"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',')]
        return []
    
    def get_file_size_display(self):
        """Retorna el tamaño del archivo en formato legible"""
        if not self.file_size:
            return "N/A"
        
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"


class ResourceBookmark(models.Model):
    """
    Marcadores de recursos guardados por los usuarios
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='resource_bookmarks',
        verbose_name='Usuario'
    )
    
    resource = models.ForeignKey(
        BestPracticeResource,
        on_delete=models.CASCADE,
        related_name='bookmarks',
        verbose_name='Recurso'
    )
    
    notes = models.TextField(
        blank=True,
        verbose_name='Notas personales',
        help_text='Notas privadas sobre este recurso'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Marcador de Recurso'
        verbose_name_plural = 'Marcadores de Recursos'
        unique_together = ['user', 'resource']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.resource.title}"