# admin_jobs/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from companies.models import Job, AuditLog, ComplianceStatus
from django.http import HttpResponseForbidden


def get_client_ip(request):
    """Obtiene la IP del cliente"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    return x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')


def admin_required(view_func):
    """Decorador personalizado para verificar que el usuario sea admin"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Debes iniciar sesión como administrador.')
            return redirect('accounts:login')
        
        if request.user.user_type != 'admin':
            messages.error(request, 'No tienes permisos para acceder a esta sección.')
            return redirect('core:dashboard')
        
        return view_func(request, *args, **kwargs)
    return wrapper


@login_required
@admin_required
def pending_jobs_list(request):
    """Lista de ofertas pendientes de revisión"""
    
    # Filtros
    status_filter = request.GET.get('status', 'pending_review')
    search_query = request.GET.get('search', '')
    
    # Query base
    jobs = Job.objects.select_related('company', 'reviewed_by').order_by('-created_at')
    
    # Aplicar filtros
    if status_filter == 'pending_review':
        jobs = jobs.filter(compliance_status=ComplianceStatus.PENDING_REVIEW)
    elif status_filter == 'changes_requested':
        jobs = jobs.filter(compliance_status=ComplianceStatus.CHANGES_REQUESTED)
    elif status_filter == 'all':
        jobs = jobs.exclude(compliance_status=ComplianceStatus.APPROVED)
    
    if search_query:
        jobs = jobs.filter(
            Q(title__icontains=search_query) |
            Q(company__username__icontains=search_query) |
            Q(company__email__icontains=search_query)
        )
    
    # Paginación
    paginator = Paginator(jobs, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'search_query': search_query,
        'total_pending': Job.objects.filter(compliance_status=ComplianceStatus.PENDING_REVIEW).count(),
        'total_changes_requested': Job.objects.filter(compliance_status=ComplianceStatus.CHANGES_REQUESTED).count(),
    }
    
    return render(request, 'admin_jobs/pending_list.html', context)


@login_required
@admin_required
def review_job_detail(request, job_id):
    """Vista detallada de una oferta para revisión"""
    job = get_object_or_404(Job, id=job_id)
    
    # Validar cumplimiento legal
    is_compliant, missing_fields = job.validate_legal_compliance()
    
    # Obtener historial de auditoría
    audit_logs = job.audit_logs.select_related('user').order_by('-timestamp')[:10]
    
    context = {
        'job': job,
        'is_compliant': is_compliant,
        'missing_fields': missing_fields,
        'missing_fields_display': job.get_missing_fields_display(),
        'audit_logs': audit_logs,
    }
    
    return render(request, 'admin_jobs/review_detail.html', context)


@login_required
@admin_required
def approve_job(request, job_id):
    """Aprobar una oferta de trabajo"""
    if request.method != 'POST':
        return HttpResponseForbidden("Método no permitido")
    
    job = get_object_or_404(Job, id=job_id)
    
    # Verificar que cumple con requisitos
    is_compliant, missing_fields = job.validate_legal_compliance()
    
    if not is_compliant:
        messages.error(
            request,
            f'❌ No se puede aprobar. Faltan campos obligatorios: {", ".join(job.get_missing_fields_display())}'
        )
        return redirect('admin_jobs:review_detail', job_id=job_id)
    
    # Aprobar la oferta
    job.approve(request.user)
    
    # Registrar en auditoría
    AuditLog.log_action(
        job=job,
        action='approved',
        user=request.user,
        details={
            'previous_status': 'pending_review',
            'new_status': 'approved',
            'compliant': True
        },
        ip_address=get_client_ip(request),
        notes=f'Oferta aprobada por {request.user.get_full_name()}'
    )
    
    messages.success(
        request,
        f'✅ Oferta "{job.title}" aprobada exitosamente. Ahora está visible públicamente.'
    )
    
    return redirect('admin_jobs:pending_list')


@login_required
@admin_required
def reject_job(request, job_id):
    """Rechazar una oferta de trabajo"""
    if request.method != 'POST':
        return HttpResponseForbidden("Método no permitido")
    
    job = get_object_or_404(Job, id=job_id)
    reason = request.POST.get('reason', '').strip()
    
    if not reason:
        messages.error(request, '❌ Debes proporcionar una razón para el rechazo.')
        return redirect('admin_jobs:review_detail', job_id=job_id)
    
    if len(reason) < 20:
        messages.error(request, '❌ La razón de rechazo debe tener al menos 20 caracteres.')
        return redirect('admin_jobs:review_detail', job_id=job_id)
    
    # Rechazar la oferta
    job.reject(request.user, reason)
    
    # Registrar en auditoría
    AuditLog.log_action(
        job=job,
        action='rejected',
        user=request.user,
        details={
            'previous_status': job.compliance_status,
            'new_status': 'rejected',
            'reason': reason
        },
        ip_address=get_client_ip(request),
        notes=f'Oferta rechazada: {reason}'
    )
    
    messages.success(
        request,
        f'❌ Oferta "{job.title}" rechazada. La empresa recibirá una notificación con el motivo.'
    )
    
    return redirect('admin_jobs:pending_list')


@login_required
@admin_required
def request_changes(request, job_id):
    """Solicitar cambios en una oferta"""
    if request.method != 'POST':
        return HttpResponseForbidden("Método no permitido")
    
    job = get_object_or_404(Job, id=job_id)
    reason = request.POST.get('reason', '').strip()
    
    if not reason:
        messages.error(request, '❌ Debes especificar qué cambios se requieren.')
        return redirect('admin_jobs:review_detail', job_id=job_id)
    
    if len(reason) < 20:
        messages.error(request, '❌ La descripción de cambios debe tener al menos 20 caracteres.')
        return redirect('admin_jobs:review_detail', job_id=job_id)
    
    # Solicitar cambios
    job.request_changes(request.user, reason)
    
    # Registrar en auditoría
    AuditLog.log_action(
        job=job,
        action='changes_requested',
        user=request.user,
        details={
            'previous_status': job.compliance_status,
            'new_status': 'changes_requested',
            'requested_changes': reason
        },
        ip_address=get_client_ip(request),
        notes=f'Cambios solicitados: {reason}'
    )
    
    messages.warning(
        request,
        f'⚠️ Cambios solicitados para "{job.title}". La empresa podrá editar y reenviar la oferta.'
    )
    
    return redirect('admin_jobs:pending_list')


@login_required
@admin_required
def audit_logs_view(request):
    """Vista de logs de auditoría"""
    
    # Filtros
    action_filter = request.GET.get('action', 'all')
    search_query = request.GET.get('search', '')
    
    # Query base
    logs = AuditLog.objects.select_related('job', 'user').order_by('-timestamp')
    
    # Aplicar filtros
    if action_filter != 'all':
        logs = logs.filter(action=action_filter)
    
    if search_query:
        logs = logs.filter(
            Q(job__title__icontains=search_query) |
            Q(user__username__icontains=search_query) |
            Q(notes__icontains=search_query)
        )
    
    # Paginación
    paginator = Paginator(logs, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Estadísticas
    stats = {
        'total_logs': AuditLog.objects.count(),
        'approved_count': AuditLog.objects.filter(action='approved').count(),
        'rejected_count': AuditLog.objects.filter(action='rejected').count(),
        'changes_requested_count': AuditLog.objects.filter(action='changes_requested').count(),
    }
    
    context = {
        'page_obj': page_obj,
        'action_filter': action_filter,
        'search_query': search_query,
        'stats': stats,
        'action_choices': AuditLog.ACTION_CHOICES,
    }
    
    return render(request, 'admin_jobs/audit_logs.html', context)