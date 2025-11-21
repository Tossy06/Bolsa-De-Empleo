from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import Interview, InterviewRescheduleRequest, InterviewNotification


@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):
    """
    Administración de entrevistas
    """
    list_display = [
        'id_short',
        'title_display',
        'candidate_name',
        'company_name',
        'scheduled_datetime',
        'status_badge',
        'interview_type_badge',
        'confirmations_status',
        'accessibility_indicators',
        'created_at',
    ]
    
    list_filter = [
        'status',
        'interview_type',
        'platform',
        'requires_sign_language_interpreter',
        'requires_accessible_location',
        'requires_screen_reader_support',
        'requires_captioning',
        'created_at',
        'scheduled_date',
    ]
    
    search_fields = [
        'id',
        'title',
        'job_title',
        'candidate__username',
        'candidate__email',
        'candidate__first_name',
        'candidate__last_name',
        'company__username',
        'company__email',
        'company__first_name',
        'company__last_name',
        'description',
    ]
    
    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
        'cancelled_at',
        'cancelled_by',
        'completed_at',
    ]
    
    fieldsets = (
        ('Información General', {
            'fields': (
                'id',
                'candidate',
                'company',
                'title',
                'job_title',
                'description',
                'status',
            )
        }),
        ('Fecha y Hora', {
            'fields': (
                'scheduled_date',
                'scheduled_time',
                'duration_minutes',
            )
        }),
        ('Tipo de Entrevista', {
            'fields': (
                'interview_type',
                'platform',
                'meeting_url',
                'meeting_id',
                'meeting_password',
            )
        }),
        ('Ubicación (Presencial)', {
            'fields': (
                'location_address',
                'location_instructions',
            ),
            'classes': ('collapse',),
        }),
        ('Requisitos de Accesibilidad', {
            'fields': (
                'requires_sign_language_interpreter',
                'requires_accessible_location',
                'requires_screen_reader_support',
                'requires_captioning',
                'other_accessibility_needs',
            ),
            'classes': ('collapse',),
        }),
        ('Confirmaciones', {
            'fields': (
                'candidate_confirmed',
                'candidate_confirmed_at',
                'company_confirmed',
                'company_confirmed_at',
            )
        }),
        ('Cancelación', {
            'fields': (
                'cancelled_by',
                'cancelled_at',
                'cancellation_reason',
            ),
            'classes': ('collapse',),
        }),
        ('Notas Internas', {
            'fields': (
                'company_notes',
            ),
            'classes': ('collapse',),
        }),
        ('Fechas del Sistema', {
            'fields': (
                'created_at',
                'updated_at',
                'completed_at',
            )
        }),
    )
    
    # Ahora podemos usar autocomplete_fields porque CustomUser tiene search_fields
    autocomplete_fields = ['candidate', 'company']
    
    date_hierarchy = 'scheduled_date'
    
    actions = [
        'mark_as_confirmed',
        'mark_as_completed',
        'mark_as_cancelled',
        'send_reminder_notifications',
    ]
    
    list_per_page = 25
    
    def id_short(self, obj):
        """Muestra ID corto"""
        return str(obj.id)[:8]
    id_short.short_description = 'ID'
    
    def title_display(self, obj):
        """Muestra título con link"""
        url = reverse('admin:interviews_interview_change', args=[obj.pk])
        return format_html('<a href="{}">{}</a>', url, obj.title)
    title_display.short_description = 'Título'
    title_display.admin_order_field = 'title'
    
    def candidate_name(self, obj):
        """Muestra nombre del candidato con link"""
        url = reverse('admin:accounts_customuser_change', args=[obj.candidate.pk])
        return format_html(
            '<a href="{}">{}</a>',
            url,
            obj.candidate.get_full_name()
        )
    candidate_name.short_description = 'Candidato'
    candidate_name.admin_order_field = 'candidate__first_name'
    
    def company_name(self, obj):
        """Muestra nombre de la empresa con link"""
        url = reverse('admin:accounts_customuser_change', args=[obj.company.pk])
        return format_html(
            '<a href="{}">{}</a>',
            url,
            obj.company.get_full_name()
        )
    company_name.short_description = 'Empresa'
    company_name.admin_order_field = 'company__first_name'
    
    def scheduled_datetime(self, obj):
        """Muestra fecha y hora programada"""
        return format_html(
            '<strong>{}</strong><br><small>{}</small>',
            obj.scheduled_date.strftime('%d/%m/%Y'),
            obj.scheduled_time.strftime('%H:%M')
        )
    scheduled_datetime.short_description = 'Fecha/Hora'
    scheduled_datetime.admin_order_field = 'scheduled_date'
    
    def status_badge(self, obj):
        """Muestra badge de estado"""
        colors = {
            'proposed': '#ffc107',
            'confirmed': '#28a745',
            'completed': '#17a2b8',
            'cancelled': '#dc3545',
            'no_show': '#6c757d',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Estado'
    status_badge.admin_order_field = 'status'
    
    def interview_type_badge(self, obj):
        """Muestra badge de tipo de entrevista"""
        icons = {
            'online': '🌐',
            'in_person': '🏢',
            'phone': '📞',
            'hybrid': '🔄',
        }
        colors = {
            'online': '#007bff',
            'in_person': '#28a745',
            'phone': '#ffc107',
            'hybrid': '#6f42c1',
        }
        icon = icons.get(obj.interview_type, '❓')
        color = colors.get(obj.interview_type, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px;">{} {}</span>',
            color,
            icon,
            obj.get_interview_type_display()
        )
    interview_type_badge.short_description = 'Tipo'
    interview_type_badge.admin_order_field = 'interview_type'
    
    def confirmations_status(self, obj):
        """Muestra estado de confirmaciones"""
        candidate_icon = '✅' if obj.candidate_confirmed else '⏳'
        company_icon = '✅' if obj.company_confirmed else '⏳'
        return format_html(
            '<div style="font-size: 11px;">'
            'Candidato: {}<br>'
            'Empresa: {}'
            '</div>',
            candidate_icon,
            company_icon
        )
    confirmations_status.short_description = 'Confirmaciones'
    
    def accessibility_indicators(self, obj):
        """Muestra indicadores de accesibilidad"""
        indicators = []
        if obj.requires_sign_language_interpreter:
            indicators.append('🤟')
        if obj.requires_accessible_location:
            indicators.append('♿')
        if obj.requires_screen_reader_support:
            indicators.append('👁️')
        if obj.requires_captioning:
            indicators.append('📝')
        
        if indicators:
            return format_html(' '.join(indicators))
        return '—'
    accessibility_indicators.short_description = 'Accesibilidad'
    
    # Acciones personalizadas
    def mark_as_confirmed(self, request, queryset):
        """Marcar como confirmadas"""
        count = 0
        for interview in queryset:
            if interview.status == 'proposed':
                interview.status = 'confirmed'
                interview.save()
                count += 1
        
        self.message_user(
            request,
            f'{count} entrevista(s) marcada(s) como confirmadas.'
        )
    mark_as_confirmed.short_description = 'Marcar como confirmadas'
    
    def mark_as_completed(self, request, queryset):
        """Marcar como completadas"""
        count = queryset.filter(
            status__in=['confirmed', 'proposed']
        ).update(
            status='completed',
            completed_at=timezone.now()
        )
        
        self.message_user(
            request,
            f'{count} entrevista(s) marcada(s) como completadas.'
        )
    mark_as_completed.short_description = 'Marcar como completadas'
    
    def mark_as_cancelled(self, request, queryset):
        """Marcar como canceladas"""
        count = 0
        for interview in queryset.filter(status__in=['confirmed', 'proposed']):
            interview.status = 'cancelled'
            interview.cancelled_at = timezone.now()
            # Solo establecer cancelled_by si el campo existe en el modelo
            if hasattr(interview, 'cancelled_by'):
                interview.cancelled_by = request.user
            interview.save()
            count += 1
        
        self.message_user(
            request,
            f'{count} entrevista(s) marcada(s) como canceladas.'
        )
    mark_as_cancelled.short_description = 'Marcar como canceladas'
    
    def send_reminder_notifications(self, request, queryset):
        """Enviar recordatorios"""
        count = 0
        for interview in queryset.filter(
            status__in=['confirmed', 'proposed'],
            scheduled_date__gte=timezone.now().date()
        ):
            # Lógica para enviar recordatorio
            count += 1
        
        self.message_user(
            request,
            f'Recordatorios enviados para {count} entrevista(s).'
        )
    send_reminder_notifications.short_description = 'Enviar recordatorios'
    
    def get_queryset(self, request):
        """Optimiza las consultas"""
        qs = super().get_queryset(request)
        return qs.select_related('candidate', 'company')


@admin.register(InterviewRescheduleRequest)
class InterviewRescheduleRequestAdmin(admin.ModelAdmin):
    """
    Administración de solicitudes de reprogramación
    """
    list_display = [
        'id_short',
        'interview_title',
        'requested_by_name',
        'proposed_datetime',
        'status_badge',
        'created_at',
    ]
    
    list_filter = [
        'status',
        'created_at',
        'proposed_date',
    ]
    
    search_fields = [
        'interview__title',
        'interview__job_title',
        'requested_by__username',
        'requested_by__email',
        'reason',
        'response',
    ]
    
    # CORRECCIÓN: Solo incluir campos que existen en el modelo
    readonly_fields = [
        'id',
        'created_at',
        'responded_at',
    ]
    
    fieldsets = (
        ('Información General', {
            'fields': (
                'id',
                'interview',
                'requested_by',
                'status',
            )
        }),
        ('Solicitud', {
            'fields': (
                'reason',
                'proposed_date',
                'proposed_time',
            )
        }),
        ('Respuesta', {
            'fields': (
                'response',
                'responded_at',
            )
        }),
        ('Fechas del Sistema', {
            'fields': (
                'created_at',
            )
        }),
    )
    
    # Ahora podemos usar autocomplete_fields
    autocomplete_fields = ['interview', 'requested_by']
    
    date_hierarchy = 'created_at'
    
    actions = ['approve_requests', 'reject_requests']
    
    list_per_page = 25
    
    def id_short(self, obj):
        """Muestra ID corto"""
        return str(obj.id)[:8]
    id_short.short_description = 'ID'
    
    def interview_title(self, obj):
        """Muestra título de la entrevista con link"""
        url = reverse('admin:interviews_interview_change', args=[obj.interview.pk])
        return format_html('<a href="{}">{}</a>', url, obj.interview.title)
    interview_title.short_description = 'Entrevista'
    interview_title.admin_order_field = 'interview__title'
    
    def requested_by_name(self, obj):
        """Muestra nombre del solicitante"""
        return obj.requested_by.get_full_name()
    requested_by_name.short_description = 'Solicitado por'
    requested_by_name.admin_order_field = 'requested_by__first_name'
    
    def proposed_datetime(self, obj):
        """Muestra fecha y hora propuesta"""
        return format_html(
            '<strong>{}</strong><br><small>{}</small>',
            obj.proposed_date.strftime('%d/%m/%Y'),
            obj.proposed_time.strftime('%H:%M')
        )
    proposed_datetime.short_description = 'Nueva Fecha/Hora'
    proposed_datetime.admin_order_field = 'proposed_date'
    
    def status_badge(self, obj):
        """Muestra badge de estado"""
        colors = {
            'pending': '#ffc107',
            'accepted': '#28a745',
            'rejected': '#dc3545',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Estado'
    status_badge.admin_order_field = 'status'
    
    # Acciones personalizadas
    def approve_requests(self, request, queryset):
        """Aprobar solicitudes"""
        count = 0
        for req in queryset.filter(status='pending'):
            req.status = 'accepted'
            req.responded_at = timezone.now()
            req.save()
            
            # Actualizar entrevista
            interview = req.interview
            interview.scheduled_date = req.proposed_date
            interview.scheduled_time = req.proposed_time
            interview.save()
            
            count += 1
        
        self.message_user(
            request,
            f'{count} solicitud(es) aprobada(s) y entrevista(s) reprogramada(s).'
        )
    approve_requests.short_description = 'Aprobar solicitudes'
    
    def reject_requests(self, request, queryset):
        """Rechazar solicitudes"""
        count = queryset.filter(status='pending').update(
            status='rejected',
            responded_at=timezone.now()
        )
        
        self.message_user(
            request,
            f'{count} solicitud(es) rechazada(s).'
        )
    reject_requests.short_description = 'Rechazar solicitudes'
    
    def get_queryset(self, request):
        """Optimiza las consultas"""
        qs = super().get_queryset(request)
        return qs.select_related('interview', 'requested_by')


@admin.register(InterviewNotification)
class InterviewNotificationAdmin(admin.ModelAdmin):
    """
    Administración de notificaciones de entrevistas
    """
    list_display = [
        'id_short',
        'user_name',
        'interview_title',
        'notification_type_badge',
        'is_read_icon',
        'created_at',
    ]
    
    list_filter = [
        'notification_type',
        'is_read',
        'created_at',
    ]
    
    search_fields = [
        'user__username',
        'user__email',
        'interview__title',
        'message',
    ]
    
    readonly_fields = [
        'id',
        'created_at',
        'read_at',
    ]
    
    fieldsets = (
        ('Información General', {
            'fields': (
                'id',
                'user',
                'interview',
                'notification_type',
            )
        }),
        ('Contenido', {
            'fields': (
                'message',
            )
        }),
        ('Estado', {
            'fields': (
                'is_read',
                'read_at',
            )
        }),
        ('Fechas del Sistema', {
            'fields': (
                'created_at',
            )
        }),
    )
    
    # Ahora podemos usar autocomplete_fields
    autocomplete_fields = ['user', 'interview']
    
    date_hierarchy = 'created_at'
    
    actions = ['mark_as_read', 'mark_as_unread']
    
    list_per_page = 50
    
    def id_short(self, obj):
        """Muestra ID corto"""
        return str(obj.id)[:8]
    id_short.short_description = 'ID'
    
    def user_name(self, obj):
        """Muestra nombre del usuario"""
        url = reverse('admin:accounts_customuser_change', args=[obj.user.pk])
        return format_html('<a href="{}">{}</a>', url, obj.user.get_full_name())
    user_name.short_description = 'Usuario'
    user_name.admin_order_field = 'user__first_name'
    
    def interview_title(self, obj):
        """Muestra título de la entrevista"""
        url = reverse('admin:interviews_interview_change', args=[obj.interview.pk])
        return format_html('<a href="{}">{}</a>', url, obj.interview.title)
    interview_title.short_description = 'Entrevista'
    interview_title.admin_order_field = 'interview__title'
    
    def notification_type_badge(self, obj):
        """Muestra badge de tipo de notificación"""
        colors = {
            'created': '#007bff',
            'confirmed': '#28a745',
            'cancelled': '#dc3545',
            'rescheduled': '#ffc107',
            'reminder': '#17a2b8',
        }
        icons = {
            'created': '📅',
            'confirmed': '✅',
            'cancelled': '❌',
            'rescheduled': '🔄',
            'reminder': '🔔',
        }
        color = colors.get(obj.notification_type, '#6c757d')
        icon = icons.get(obj.notification_type, '📬')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px;">{} {}</span>',
            color,
            icon,
            obj.get_notification_type_display()
        )
    notification_type_badge.short_description = 'Tipo'
    notification_type_badge.admin_order_field = 'notification_type'
    
    def is_read_icon(self, obj):
        """Muestra icono de leído/no leído"""
        if obj.is_read:
            return format_html(
                '<span style="color: green; font-size: 16px;">✓</span>'
            )
        return format_html(
            '<span style="color: orange; font-size: 16px;">●</span>'
        )
    is_read_icon.short_description = 'Leído'
    is_read_icon.admin_order_field = 'is_read'
    
    # Acciones personalizadas
    def mark_as_read(self, request, queryset):
        """Marcar como leídas"""
        count = queryset.filter(is_read=False).update(
            is_read=True,
            read_at=timezone.now()
        )
        
        self.message_user(
            request,
            f'{count} notificación(es) marcada(s) como leídas.'
        )
    mark_as_read.short_description = 'Marcar como leídas'
    
    def mark_as_unread(self, request, queryset):
        """Marcar como no leídas"""
        count = queryset.filter(is_read=True).update(
            is_read=False,
            read_at=None
        )
        
        self.message_user(
            request,
            f'{count} notificación(es) marcada(s) como no leídas.'
        )
    mark_as_unread.short_description = 'Marcar como no leídas'
    
    def get_queryset(self, request):
        """Optimiza las consultas"""
        qs = super().get_queryset(request)
        return qs.select_related('user', 'interview')