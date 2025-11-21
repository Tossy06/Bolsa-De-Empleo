# training/models.py
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify

class SocialSkillsCourse(models.Model):
    """
    Modelo para cursos de habilidades sociales
    """
    
    DIFFICULTY_CHOICES = [
        ('beginner', 'Principiante'),
        ('intermediate', 'Intermedio'),
        ('advanced', 'Avanzado'),
    ]
    
    CATEGORY_CHOICES = [
        ('communication', 'Comunicación'),
        ('teamwork', 'Trabajo en Equipo'),
        ('problem_solving', 'Resolución de Problemas'),
        ('leadership', 'Liderazgo'),
        ('conflict_resolution', 'Resolución de Conflictos'),
        ('time_management', 'Gestión del Tiempo'),
    ]
    
    title = models.CharField(
        max_length=200,
        verbose_name='Título del curso'
    )
    
    slug = models.SlugField(
        max_length=250,
        unique=True,
        blank=True
    )
    
    description = models.TextField(
        verbose_name='Descripción',
        help_text='Descripción detallada del curso'
    )
    
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default='communication',
        verbose_name='Categoría'
    )
    
    difficulty = models.CharField(
        max_length=20,
        choices=DIFFICULTY_CHOICES,
        default='beginner',
        verbose_name='Nivel de dificultad'
    )
    
    duration_hours = models.PositiveIntegerField(
        default=1,
        verbose_name='Duración (horas estimadas)',
        validators=[MinValueValidator(1)]
    )
    
    thumbnail = models.ImageField(
        upload_to='courses/thumbnails/',
        blank=True,
        null=True,
        verbose_name='Imagen de portada'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Curso activo'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Orden para mostrar en el listado
    order = models.PositiveIntegerField(
        default=0,
        verbose_name='Orden de visualización'
    )
    
    class Meta:
        verbose_name = 'Curso de Habilidades Sociales'
        verbose_name_plural = 'Cursos de Habilidades Sociales'
        ordering = ['order', 'title']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def get_total_lessons(self):
        """Retorna el número total de lecciones"""
        return self.lessons.count()
    
    def get_enrolled_count(self):
        """Retorna el número de candidatos inscritos"""
        return self.enrollments.filter(status='enrolled').count()


class CourseLesson(models.Model):
    """
    Lecciones/módulos dentro de un curso
    """
    
    CONTENT_TYPE_CHOICES = [
        ('video', 'Video'),
        ('text', 'Texto/Lectura'),
        ('quiz', 'Cuestionario'),
        ('interactive', 'Actividad Interactiva'),
    ]
    
    course = models.ForeignKey(
        SocialSkillsCourse,
        on_delete=models.CASCADE,
        related_name='lessons',
        verbose_name='Curso'
    )
    
    title = models.CharField(
        max_length=200,
        verbose_name='Título de la lección'
    )
    
    content_type = models.CharField(
        max_length=20,
        choices=CONTENT_TYPE_CHOICES,
        default='text',
        verbose_name='Tipo de contenido'
    )
    
    content = models.TextField(
        verbose_name='Contenido de la lección',
        help_text='Contenido textual o descripción del video'
    )
    
    # Para videos (simulado)
    video_url = models.URLField(
        blank=True,
        null=True,
        verbose_name='URL del video',
        help_text='URL del video (simulado - no funcional en esta versión)'
    )
    
    video_duration_minutes = models.PositiveIntegerField(
        default=0,
        verbose_name='Duración del video (minutos)',
        help_text='Solo informativo'
    )
    
    # Transcripciones para accesibilidad
    transcript = models.TextField(
        blank=True,
        verbose_name='Transcripción',
        help_text='Transcripción del video o contenido adicional para accesibilidad'
    )
    
    order = models.PositiveIntegerField(
        default=0,
        verbose_name='Orden en el curso'
    )
    
    is_mandatory = models.BooleanField(
        default=True,
        verbose_name='Lección obligatoria'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Lección'
        verbose_name_plural = 'Lecciones'
        ordering = ['course', 'order']
        unique_together = ['course', 'order']
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"


class CourseEnrollment(models.Model):
    """
    Inscripción y progreso de un candidato en un curso
    """
    
    STATUS_CHOICES = [
        ('enrolled', 'Inscrito'),
        ('in_progress', 'En Progreso'),
        ('completed', 'Completado'),
        ('dropped', 'Abandonado'),
    ]
    
    candidate = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='course_enrollments',
        verbose_name='Candidato',
        limit_choices_to={'user_type': 'candidate'}
    )
    
    course = models.ForeignKey(
        SocialSkillsCourse,
        on_delete=models.CASCADE,
        related_name='enrollments',
        verbose_name='Curso'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='enrolled',
        verbose_name='Estado'
    )
    
    progress_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name='Progreso (%)'
    )
    
    enrolled_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de inscripción'
    )
    
    started_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Fecha de inicio'
    )
    
    completed_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Fecha de finalización'
    )
    
    last_accessed_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Último acceso'
    )
    
    # Certificado
    certificate_issued = models.BooleanField(
        default=False,
        verbose_name='Certificado emitido'
    )
    
    certificate_number = models.CharField(
        max_length=50,
        blank=True,
        unique=True,
        null=True,
        verbose_name='Número de certificado'
    )
    
    class Meta:
        verbose_name = 'Inscripción a Curso'
        verbose_name_plural = 'Inscripciones a Cursos'
        ordering = ['-enrolled_at']
        unique_together = ['candidate', 'course']
    
    def __str__(self):
        return f"{self.candidate.get_full_name()} - {self.course.title}"
    
    def calculate_progress(self):
        """Calcula el progreso basado en lecciones completadas"""
        total_lessons = self.course.lessons.count()
        if total_lessons == 0:
            return 0
        
        completed_lessons = self.lesson_progress.filter(completed=True).count()
        progress = (completed_lessons / total_lessons) * 100
        
        self.progress_percentage = round(progress, 2)
        
        # Actualizar estado
        if progress >= 100:
            self.status = 'completed'
            if not self.completed_at:
                from django.utils import timezone
                self.completed_at = timezone.now()
                self.issue_certificate()
        elif progress > 0:
            self.status = 'in_progress'
            if not self.started_at:
                from django.utils import timezone
                self.started_at = timezone.now()
        
        self.save()
        return self.progress_percentage
    
    def issue_certificate(self):
        """Emite un certificado al completar el curso"""
        if not self.certificate_issued:
            import uuid
            self.certificate_number = f"CERT-{uuid.uuid4().hex[:8].upper()}"
            self.certificate_issued = True
            self.save()


class LessonProgress(models.Model):
    """
    Progreso individual de cada lección
    """
    
    enrollment = models.ForeignKey(
        CourseEnrollment,
        on_delete=models.CASCADE,
        related_name='lesson_progress',
        verbose_name='Inscripción'
    )
    
    lesson = models.ForeignKey(
        CourseLesson,
        on_delete=models.CASCADE,
        related_name='progress_records',
        verbose_name='Lección'
    )
    
    completed = models.BooleanField(
        default=False,
        verbose_name='Completada'
    )
    
    completed_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Fecha de finalización'
    )
    
    time_spent_minutes = models.PositiveIntegerField(
        default=0,
        verbose_name='Tiempo dedicado (minutos)'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Progreso de Lección'
        verbose_name_plural = 'Progreso de Lecciones'
        unique_together = ['enrollment', 'lesson']
    
    def __str__(self):
        status = "✓" if self.completed else "○"
        return f"{status} {self.enrollment.candidate.get_full_name()} - {self.lesson.title}"
    
    def mark_as_completed(self):
        """Marca la lección como completada"""
        if not self.completed:
            from django.utils import timezone
            self.completed = True
            self.completed_at = timezone.now()
            self.save()
            
            # Recalcular progreso del curso
            self.enrollment.calculate_progress()