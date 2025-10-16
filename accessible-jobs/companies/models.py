# jobs/models.py
from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone


# ========================================
# ENUMERACIONES (más limpias y mantenibles)
# ========================================

class JobType(models.TextChoices):
    FULL_TIME = 'full_time', 'Tiempo completo'
    PART_TIME = 'part_time', 'Tiempo parcial'
    CONTRACT = 'contract', 'Por contrato'
    INTERNSHIP = 'internship', 'Prácticas'
    REMOTE = 'remote', 'Remoto'


class ExperienceLevel(models.TextChoices):
    ENTRY = 'entry', 'Sin experiencia'
    JUNIOR = 'junior', 'Junior (1-2 años)'
    MID = 'mid', 'Intermedio (3-5 años)'
    SENIOR = 'senior', 'Senior (5+ años)'


class DisabilityCategory(models.TextChoices):
    VISUAL = 'visual', 'Discapacidad visual'
    HEARING = 'hearing', 'Discapacidad auditiva'
    PHYSICAL = 'physical', 'Discapacidad física/motriz'
    COGNITIVE = 'cognitive', 'Discapacidad cognitiva'
    INTELLECTUAL = 'intellectual', 'Discapacidad intelectual'
    PSYCHOSOCIAL = 'psychosocial', 'Discapacidad psicosocial'
    MULTIPLE = 'multiple', 'Discapacidad múltiple'
    ALL = 'all', 'Todas las discapacidades'


class ComplianceStatus(models.TextChoices):
    DRAFT = 'draft', 'Borrador'
    PENDING_REVIEW = 'pending_review', 'Pendiente de revisión'
    APPROVED = 'approved', 'Aprobada'
    REJECTED = 'rejected', 'Rechazada'
    CHANGES_REQUESTED = 'changes_requested', 'Cambios solicitados'
    
class Job(models.Model):
    # --- Campos principales ---
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
    is_remote = models.BooleanField(default=False, verbose_name="¿Es trabajo remoto?")
    job_type = models.CharField(
        max_length=20,
        choices=JobType.choices,
        default=JobType.FULL_TIME,
        verbose_name="Tipo de empleo"
    )
    experience_level = models.CharField(
        max_length=20,
        choices=ExperienceLevel.choices,
        default=ExperienceLevel.ENTRY,
        verbose_name="Nivel de experiencia requerido"
    )
    salary_min = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        verbose_name="Salario mínimo"
    )
    salary_max = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        verbose_name="Salario máximo"
    )
    disability_focus = models.CharField(
        max_length=20,
        choices=DisabilityCategory.choices,
        default=DisabilityCategory.ALL,
        verbose_name="Enfoque en discapacidad"
    )
    accessibility_features = models.TextField(
        blank=True,
        verbose_name="Características de accesibilidad",
        help_text="Describe las adaptaciones y características de accesibilidad disponibles"
    )
    benefits = models.TextField(blank=True, verbose_name="Beneficios adicionales")
    application_deadline = models.DateField(null=True, blank=True, verbose_name="Fecha límite para aplicar")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, verbose_name="¿Está activa?")
    featured = models.BooleanField(default=False, verbose_name="Destacar oferta")

    # --- Cumplimiento legal ---
    reasonable_accommodations = models.TextField(
        blank=True,
        verbose_name="Ajustes razonables disponibles",
        help_text="Describe los ajustes razonables que la empresa puede proporcionar (OBLIGATORIO según Ley 1618)"
    )
    workplace_accessibility = models.TextField(
        blank=True,
        verbose_name="Condiciones de accesibilidad del lugar de trabajo",
        help_text="Describe las características de accesibilidad física y tecnológica (OBLIGATORIO)"
    )
    non_discrimination_statement = models.TextField(
        blank=True,
        verbose_name="Declaración de no discriminación",
        help_text="Declaración explícita de políticas de inclusión y no discriminación (OBLIGATORIO)"
    )
    compliance_status = models.CharField(
        max_length=20,
        choices=ComplianceStatus.choices,
        default=ComplianceStatus.DRAFT,
        verbose_name="Estado de cumplimiento legal",
        help_text="Estado de validación de cumplimiento normativo"
    )
    rejection_reason = models.TextField(
        blank=True,
        verbose_name="Razón de rechazo",
        help_text="Motivo por el cual la oferta fue rechazada o requiere cambios"
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="reviewed_jobs",
        verbose_name="Revisado por"
    )
    reviewed_at = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de revisión")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Oferta de trabajo"
        verbose_name_plural = "Ofertas de trabajo"
        indexes = [
            models.Index(fields=['compliance_status']),
            models.Index(fields=['is_active', 'compliance_status']),
        ]

    def __str__(self):
        return f"{self.title} - {self.company}"

    def get_absolute_url(self):
        return reverse('jobs:detail', kwargs={'pk': self.pk})

    # --- Propiedades útiles ---
    @property
    def salary_range(self):
        if self.salary_min and self.salary_max:
            return f"${self.salary_min:,.0f} - ${self.salary_max:,.0f}"
        return f"Desde ${self.salary_min:,.0f}" if self.salary_min else (
            f"Hasta ${self.salary_max:,.0f}" if self.salary_max else "Salario a convenir"
        )

    def is_expired(self):
        return bool(self.application_deadline and timezone.now().date() > self.application_deadline)

    # --- Validaciones de cumplimiento ---
    def validate_legal_compliance(self):
        required_fields = [
            'reasonable_accommodations',
            'workplace_accessibility',
            'non_discrimination_statement'
        ]
        missing_fields = [f for f in required_fields if not (getattr(self, f, None) or '').strip()]
        return len(missing_fields) == 0, missing_fields

    def get_missing_fields_display(self):
        field_names = {
            'reasonable_accommodations': 'Ajustes razonables disponibles',
            'workplace_accessibility': 'Condiciones de accesibilidad del lugar de trabajo',
            'non_discrimination_statement': 'Declaración de no discriminación',
        }
        _, missing_fields = self.validate_legal_compliance()
        return [field_names.get(f, f) for f in missing_fields]

    def is_compliant(self):
        is_valid, _ = self.validate_legal_compliance()
        return is_valid

    # --- Gestión de estados de cumplimiento ---
    def mark_as_pending_review(self):
        self.compliance_status = ComplianceStatus.PENDING_REVIEW
        self.save(update_fields=['compliance_status', 'updated_at'])

    def _update_status(self, status, admin_user, is_active, reason=''):
        self.compliance_status = status
        self.reviewed_by = admin_user
        self.reviewed_at = timezone.now()
        self.is_active = is_active
        self.rejection_reason = reason
        self.save(update_fields=[
            'compliance_status', 'reviewed_by', 'reviewed_at',
            'is_active', 'rejection_reason', 'updated_at'
        ])

    def approve(self, admin_user):
        self._update_status(ComplianceStatus.APPROVED, admin_user, True)

    def reject(self, admin_user, reason):
        self._update_status(ComplianceStatus.REJECTED, admin_user, False, reason)

    def request_changes(self, admin_user, reason):
        self._update_status(ComplianceStatus.CHANGES_REQUESTED, admin_user, False, reason)

    def can_be_published(self):
        return self.is_active and self.compliance_status == ComplianceStatus.APPROVED and not self.is_expired()


# ========================================
# MODELO DE AUDITORÍA
# ========================================

class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('created', 'Oferta creada'),
        ('submitted', 'Oferta enviada para revisión'),
        ('validated', 'Validación realizada'),
        ('approved', 'Oferta aprobada'),
        ('rejected', 'Oferta rechazada'),
        ('changes_requested', 'Cambios solicitados'),
        ('resubmitted', 'Oferta reenviada'),
        ('updated', 'Oferta actualizada'),
        ('deactivated', 'Oferta desactivada'),
    ]

    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name='audit_logs',
        verbose_name="Oferta de trabajo"
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, verbose_name="Acción realizada")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Usuario"
    )
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Fecha y hora", db_index=True)
    details = models.JSONField(default=dict, blank=True, verbose_name="Detalles adicionales")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="Dirección IP")
    notes = models.TextField(blank=True, verbose_name="Notas adicionales")

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Registro de auditoría"
        verbose_name_plural = "Registros de auditoría"
        indexes = [
            models.Index(fields=['job', '-timestamp']),
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['action', '-timestamp']),
        ]

    def __str__(self):
        return f"{self.get_action_display()} - {self.job.title} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

    @classmethod
    def log_action(cls, job, action, user, details=None, ip_address=None, notes=''):
        return cls.objects.create(
            job=job,
            action=action,
            user=user,
            details=details or {},
            ip_address=ip_address,
            notes=notes
        )
