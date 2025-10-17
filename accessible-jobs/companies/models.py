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

class DisabilityType(models.TextChoices):
    """Tipos de discapacidad codificados para privacidad"""
    TYPE_A = 'type_a', 'Tipo A - Visual'
    TYPE_B = 'type_b', 'Tipo B - Auditiva'
    TYPE_C = 'type_c', 'Tipo C - Física/Motriz'
    TYPE_D = 'type_d', 'Tipo D - Cognitiva'
    TYPE_E = 'type_e', 'Tipo E - Intelectual'
    TYPE_F = 'type_f', 'Tipo F - Psicosocial'
    TYPE_G = 'type_g', 'Tipo G - Múltiple'


class HiringReportStatus(models.TextChoices):
    """Estados del informe de contratación"""
    PENDING = 'pending', 'Pendiente de envío'
    SENT = 'sent', 'Enviado'
    CONFIRMED = 'confirmed', 'Confirmado por Ministerio'
    FAILED = 'failed', 'Falló el envío'
    RETRY = 'retry', 'Reintentando'


class HiringReport(models.Model):
    """
    Modelo para registrar contrataciones de personas con discapacidad
    y generar informes para el Ministerio de Trabajo (Ley 2466/2025)
    """
    # Información de la empresa
    company = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='hiring_reports',
        verbose_name='Empresa'
    )
    company_name = models.CharField(max_length=200, verbose_name='Nombre de la empresa')
    company_nit = models.CharField(max_length=50, verbose_name='NIT de la empresa')
    
    # Información del contrato (anonimizada para privacidad)
    job = models.ForeignKey(
        'Job',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='hiring_reports',
        verbose_name='Oferta de trabajo'
    )
    contract_number = models.CharField(max_length=100, verbose_name='Número de contrato')
    contract_date = models.DateField(verbose_name='Fecha de contrato')
    position_title = models.CharField(max_length=200, verbose_name='Cargo')
    
    # Información de discapacidad (codificada)
    disability_type = models.CharField(
        max_length=20,
        choices=DisabilityType.choices,
        verbose_name='Tipo de discapacidad (codificado)'
    )
    disability_percentage = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='Porcentaje de discapacidad'
    )
    
    # Estado del informe
    status = models.CharField(
        max_length=20,
        choices=HiringReportStatus.choices,
        default=HiringReportStatus.PENDING,
        verbose_name='Estado del informe'
    )
    
    # Archivos generados
    pdf_file = models.FileField(
        upload_to='hiring_reports/pdf/%Y/%m/',
        null=True,
        blank=True,
        verbose_name='Archivo PDF'
    )
    xml_file = models.FileField(
        upload_to='hiring_reports/xml/%Y/%m/',
        null=True,
        blank=True,
        verbose_name='Archivo XML'
    )
    digital_signature = models.TextField(
        blank=True,
        verbose_name='Firma digital',
        help_text='Hash SHA-256 del documento'
    )
    
    # Control de envío
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de envío')
    confirmed_at = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de confirmación')
    retry_count = models.IntegerField(default=0, verbose_name='Intentos de envío')
    last_retry_at = models.DateTimeField(null=True, blank=True, verbose_name='Último intento')
    
    # Respuesta del Ministerio
    ministry_response = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Respuesta del Ministerio'
    )
    ministry_receipt_number = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Número de recibo del Ministerio'
    )
    
    # Notas y errores
    notes = models.TextField(blank=True, verbose_name='Notas adicionales')
    error_log = models.TextField(blank=True, verbose_name='Registro de errores')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Creado el')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Actualizado el')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Informe de contratación'
        verbose_name_plural = 'Informes de contratación'
        indexes = [
            models.Index(fields=['company', '-created_at']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['contract_number']),
        ]
    
    def __str__(self):
        return f"Informe {self.contract_number} - {self.company_name} - {self.get_status_display()}"
    
    def generate_signature(self):
        """Genera la firma digital del informe"""
        import hashlib
        from datetime import datetime
        
        data = f"{self.company_nit}{self.contract_number}{self.contract_date}{self.disability_type}"
        signature = hashlib.sha256(data.encode()).hexdigest()
        self.digital_signature = signature
        self.save(update_fields=['digital_signature'])
        return signature
    
    def can_retry(self):
        """Verifica si se puede reintentar el envío"""
        return self.retry_count < 3 and self.status in [
            HiringReportStatus.FAILED,
            HiringReportStatus.RETRY
        ]
    
    def mark_as_sent(self):
        """Marca el informe como enviado"""
        self.status = HiringReportStatus.SENT
        self.sent_at = timezone.now()
        self.save(update_fields=['status', 'sent_at', 'updated_at'])
    
    def mark_as_confirmed(self, receipt_number, response_data=None):
        """Marca el informe como confirmado por el Ministerio"""
        self.status = HiringReportStatus.CONFIRMED
        self.confirmed_at = timezone.now()
        self.ministry_receipt_number = receipt_number
        if response_data:
            self.ministry_response = response_data
        self.save(update_fields=[
            'status', 'confirmed_at', 'ministry_receipt_number',
            'ministry_response', 'updated_at'
        ])
    
    def mark_as_failed(self, error_message):
        """Marca el informe como fallido"""
        self.status = HiringReportStatus.FAILED
        self.error_log += f"\n[{timezone.now()}] {error_message}"
        self.last_retry_at = timezone.now()
        self.save(update_fields=['status', 'error_log', 'last_retry_at', 'updated_at'])
    
    def increment_retry(self):
        """Incrementa el contador de reintentos"""
        self.retry_count += 1
        self.status = HiringReportStatus.RETRY
        self.last_retry_at = timezone.now()
        self.save(update_fields=['retry_count', 'status', 'last_retry_at', 'updated_at'])


class EmployeeQuotaTracking(models.Model):
    """
    Modelo para rastrear el cumplimiento de cuotas de empleo
    según Ley 2466/2025 (2% de empleados con discapacidad)
    """
    company = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='quota_tracking',
        verbose_name='Empresa'
    )
    
    # Información actual de empleados
    total_employees = models.PositiveIntegerField(
        default=0,
        verbose_name='Total de empleados',
        help_text='Número total de empleados en la empresa'
    )
    
    employees_with_disability = models.PositiveIntegerField(
        default=0,
        verbose_name='Empleados con discapacidad',
        help_text='Número de empleados con discapacidad actualmente contratados'
    )
    
    # Histórico por periodo
    last_updated = models.DateTimeField(
        auto_now=True,
        verbose_name='Última actualización'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Seguimiento de Cuotas'
        verbose_name_plural = 'Seguimiento de Cuotas'
    
    def __str__(self):
        return f"Cuotas {self.company.get_full_name()} - {self.compliance_percentage}%"
    
    @property
    def required_employees_with_disability(self):
        """
        Calcula cuántos empleados con discapacidad se requieren según la ley
        Ley 2466/2025: 2% del total de empleados (mínimo 2 por cada 100)
        """
        if self.total_employees < 50:
            return 0  # Empresas pequeñas pueden estar exentas
        
        # 2% del total, redondeado hacia arriba
        import math
        required = math.ceil(self.total_employees * 0.02)
        
        # Mínimo 1 si tiene más de 50 empleados
        return max(1, required)
    
    @property
    def compliance_percentage(self):
        """Porcentaje de cumplimiento actual"""
        if self.required_employees_with_disability == 0:
            return 100.0
        
        return round(
            (self.employees_with_disability / self.required_employees_with_disability) * 100,
            2
        )
    
    @property
    def is_compliant(self):
        """¿Cumple con la cuota legal?"""
        return self.employees_with_disability >= self.required_employees_with_disability
    
    @property
    def employees_needed(self):
        """Cuántos empleados con discapacidad faltan para cumplir"""
        deficit = self.required_employees_with_disability - self.employees_with_disability
        return max(0, deficit)
    
    @property
    def compliance_status(self):
        """Estado de cumplimiento: 'compliant', 'warning', 'critical'"""
        percentage = self.compliance_percentage
        
        if percentage >= 100:
            return 'compliant'
        elif percentage >= 75:
            return 'warning'
        else:
            return 'critical'
    
    def update_from_reports(self):
        """
        Actualiza automáticamente desde los HiringReports confirmados
        """
        from companies.models import HiringReport, HiringReportStatus
        
        confirmed_reports = HiringReport.objects.filter(
            company=self.company,
            status=HiringReportStatus.CONFIRMED
        )
        
        self.employees_with_disability = confirmed_reports.count()
        self.save()
        
        return self.employees_with_disability


class QuotaHistoricalRecord(models.Model):
    """
    Registro histórico mensual de cumplimiento de cuotas
    """
    company = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='quota_history',
        verbose_name='Empresa'
    )
    
    period = models.DateField(
        verbose_name='Periodo',
        help_text='Fecha del periodo (primer día del mes)'
    )
    
    total_employees = models.PositiveIntegerField(verbose_name='Total empleados')
    employees_with_disability = models.PositiveIntegerField(verbose_name='Empleados con discapacidad')
    required_employees = models.PositiveIntegerField(verbose_name='Empleados requeridos')
    compliance_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name='Porcentaje de cumplimiento'
    )
    is_compliant = models.BooleanField(default=False, verbose_name='¿Cumple?')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-period']
        unique_together = ['company', 'period']
        verbose_name = 'Registro Histórico de Cuotas'
        verbose_name_plural = 'Registros Históricos de Cuotas'
    
    def __str__(self):
        return f"{self.company} - {self.period.strftime('%m/%Y')} - {self.compliance_percentage}%"
    
    @classmethod
    def create_monthly_snapshot(cls, company, period=None):
        """Crear snapshot mensual del estado de cuotas"""
        from datetime import datetime
        from dateutil.relativedelta import relativedelta
        
        if period is None:
            # Primer día del mes actual
            now = datetime.now()
            period = datetime(now.year, now.month, 1).date()
        
        tracking = company.quota_tracking
        
        return cls.objects.create(
            company=company,
            period=period,
            total_employees=tracking.total_employees,
            employees_with_disability=tracking.employees_with_disability,
            required_employees=tracking.required_employees_with_disability,
            compliance_percentage=tracking.compliance_percentage,
            is_compliant=tracking.is_compliant
        )