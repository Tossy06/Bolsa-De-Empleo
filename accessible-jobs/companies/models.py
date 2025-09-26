# jobs/models.py
from django.conf import settings
from django.db import models
from django.urls import reverse

class Job(models.Model):
    JOB_TYPES = [
        ('full_time', 'Tiempo completo'),
        ('part_time', 'Tiempo parcial'),
        ('contract', 'Por contrato'),
        ('internship', 'Prácticas'),
        ('remote', 'Remoto'),
    ]
    
    EXPERIENCE_LEVELS = [
        ('entry', 'Sin experiencia'),
        ('junior', 'Junior (1-2 años)'),
        ('mid', 'Intermedio (3-5 años)'),
        ('senior', 'Senior (5+ años)'),
    ]
    
    DISABILITY_CATEGORIES = [
        ('visual', 'Discapacidad visual'),
        ('hearing', 'Discapacidad auditiva'),
        ('physical', 'Discapacidad física/motriz'),
        ('cognitive', 'Discapacidad cognitiva'),
        ('intellectual', 'Discapacidad intelectual'),
        ('psychosocial', 'Discapacidad psicosocial'),
        ('multiple', 'Discapacidad múltiple'),
        ('all', 'Todas las discapacidades'),
    ]

    company = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="jobs"
    )
    title = models.CharField(max_length=200, verbose_name="Título del puesto")
    description = models.TextField(verbose_name="Descripción del trabajo")
    responsibilities = models.TextField(
        verbose_name="Responsabilidades principales",
        help_text="Describe las tareas y responsabilidades del puesto"
    )
    requirements = models.TextField(
        verbose_name="Requisitos",
        help_text="Educación, experiencia y habilidades requeridas"
    )
    location = models.CharField(max_length=200, verbose_name="Ubicación")
    is_remote = models.BooleanField(
        default=False, 
        verbose_name="¿Es trabajo remoto?"
    )
    job_type = models.CharField(
        max_length=20,
        choices=JOB_TYPES,
        default='full_time',
        verbose_name="Tipo de empleo"
    )
    experience_level = models.CharField(
        max_length=20,
        choices=EXPERIENCE_LEVELS,
        default='entry',
        verbose_name="Nivel de experiencia requerido"
    )
    salary_min = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name="Salario mínimo"
    )
    salary_max = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name="Salario máximo"
    )
    disability_focus = models.CharField(
        max_length=20,
        choices=DISABILITY_CATEGORIES,
        default='all',
        verbose_name="Enfoque en discapacidad"
    )
    accessibility_features = models.TextField(
        blank=True,
        verbose_name="Características de accesibilidad",
        help_text="Describe las adaptaciones y características de accesibilidad disponibles"
    )
    benefits = models.TextField(
        blank=True,
        verbose_name="Beneficios adicionales"
    )
    application_deadline = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fecha límite para aplicar"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, verbose_name="¿Está activa?")
    featured = models.BooleanField(
        default=False,
        verbose_name="Destacar oferta"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Oferta de trabajo"
        verbose_name_plural = "Ofertas de trabajo"

    def __str__(self):
        return f"{self.title} - {self.company}"

    def get_absolute_url(self):
        return reverse('jobs:detail', kwargs={'pk': self.pk})

    @property
    def salary_range(self):
        if self.salary_min and self.salary_max:
            return f"${self.salary_min:,.0f} - ${self.salary_max:,.0f}"
        elif self.salary_min:
            return f"Desde ${self.salary_min:,.0f}"
        elif self.salary_max:
            return f"Hasta ${self.salary_max:,.0f}"
        return "Salario a convenir"

    def is_expired(self):
        if self.application_deadline:
            from django.utils import timezone
            return timezone.now().date() > self.application_deadline
        return False