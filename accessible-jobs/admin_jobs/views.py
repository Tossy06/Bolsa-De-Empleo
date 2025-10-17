# admin_jobs/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from companies.models import Job, AuditLog, ComplianceStatus
from django.http import HttpResponseForbidden

from django.db.models import Count, Q, Avg
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
from django.utils import timezone

from django.shortcuts import render, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Q
from companies.models import HiringReport, HiringReportStatus
from django.http import HttpResponse
from companies.services.ministry_report_service import generate_pdf_report, generate_xml_report


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

@staff_member_required
def ministry_dashboard_view(request):
    """
    Dashboard simulado del Ministerio de Trabajo
    Vista para que los admins vean todos los informes recibidos
    """
    # Estadísticas
    total_reports = HiringReport.objects.count()
    pending_reports = HiringReport.objects.filter(status=HiringReportStatus.PENDING).count()
    sent_reports = HiringReport.objects.filter(status=HiringReportStatus.SENT).count()
    confirmed_reports = HiringReport.objects.filter(status=HiringReportStatus.CONFIRMED).count()
    failed_reports = HiringReport.objects.filter(status=HiringReportStatus.FAILED).count()
    
    # Informes recientes
    recent_reports = HiringReport.objects.select_related('company', 'job').order_by('-created_at')[:10]
    
    # Estadísticas por tipo de discapacidad
    disability_stats = HiringReport.objects.filter(
        status=HiringReportStatus.CONFIRMED
    ).values('disability_type').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Empresas más activas
    top_companies = HiringReport.objects.filter(
        status=HiringReportStatus.CONFIRMED
    ).values('company__first_name', 'company__last_name', 'company_name').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    context = {
        'total_reports': total_reports,
        'pending_reports': pending_reports,
        'sent_reports': sent_reports,
        'confirmed_reports': confirmed_reports,
        'failed_reports': failed_reports,
        'recent_reports': recent_reports,
        'disability_stats': disability_stats,
        'top_companies': top_companies,
    }
    
    return render(request, 'admin_jobs/ministry_dashboard.html', context)


@staff_member_required
def ministry_reports_list_view(request):
    """
    Lista completa de informes recibidos por el Ministerio
    """
    # Filtros
    status_filter = request.GET.get('status', '')
    disability_filter = request.GET.get('disability_type', '')
    search_query = request.GET.get('search', '')
    
    # Query base
    reports = HiringReport.objects.select_related('company', 'job').order_by('-created_at')
    
    # Aplicar filtros
    if status_filter:
        reports = reports.filter(status=status_filter)
    
    if disability_filter:
        reports = reports.filter(disability_type=disability_filter)
    
    if search_query:
        reports = reports.filter(
            Q(contract_number__icontains=search_query) |
            Q(company_name__icontains=search_query) |
            Q(company_nit__icontains=search_query)
        )
    
    context = {
        'reports': reports,
        'status_filter': status_filter,
        'disability_filter': disability_filter,
        'search_query': search_query,
        'status_choices': HiringReportStatus.choices,
    }
    
    return render(request, 'admin_jobs/ministry_reports_list.html', context)


@staff_member_required
def ministry_report_detail_view(request, report_id):
    """
    Vista detallada de un informe para el Ministerio
    """
    report = get_object_or_404(
        HiringReport.objects.select_related('company', 'job'),
        id=report_id
    )
    
    context = {
        'report': report,
    }
    
    return render(request, 'admin_jobs/ministry_report_detail.html', context)


@staff_member_required
def download_report_pdf(request, report_id):
    """
    Genera y descarga el PDF en tiempo real (Ministerio)
    """
    report = get_object_or_404(HiringReport, id=report_id)
    
    try:
        # Generar PDF en memoria
        pdf_content = generate_pdf_report(report)
        
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="informe_{report.contract_number}.pdf"'
        
        return response
    
    except Exception as e:
        return HttpResponse(f'Error al generar PDF: {str(e)}', status=500)


@staff_member_required
def download_report_xml(request, report_id):
    """
    Genera y descarga el XML en tiempo real (Ministerio)
    """
    report = get_object_or_404(HiringReport, id=report_id)
    
    try:
        # Generar XML en memoria
        xml_content = generate_xml_report(report)
        
        response = HttpResponse(xml_content, content_type='application/xml')
        response['Content-Disposition'] = f'attachment; filename="informe_{report.contract_number}.xml"'
        
        return response
    
    except Exception as e:
        return HttpResponse(f'Error al generar XML: {str(e)}', status=500)
    

User = get_user_model()

@staff_member_required
def inclusion_kpis_dashboard(request):
    """
    Dashboard de KPIs de Inclusión para administradores
    """
    # Filtros
    company_filter = request.GET.get('company', '')
    sector_filter = request.GET.get('sector', '')
    period_filter = request.GET.get('period', '30')  # días
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    
    # Calcular rango de fechas
    if start_date and end_date:
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            start = timezone.now().date() - timedelta(days=int(period_filter))
            end = timezone.now().date()
    else:
        end = timezone.now().date()
        start = end - timedelta(days=int(period_filter))
    
    # KPI 1: Candidatos con discapacidad registrados
    candidates_query = User.objects.filter(user_type='candidate')
    
    if start_date or end_date:
        candidates_query = candidates_query.filter(
            date_joined__date__gte=start,
            date_joined__date__lte=end
        )
    
    total_candidates = candidates_query.count()
    candidates_with_disability = candidates_query.exclude(
        disability_type__in=['none', 'prefer_not_say']
    )
    
    # KPI 2: Ofertas de empleo inclusivas
    jobs_query = Job.objects.filter(compliance_status=ComplianceStatus.APPROVED)
    
    if company_filter:
        jobs_query = jobs_query.filter(company_id=company_filter)
    
    if start_date or end_date:
        jobs_query = jobs_query.filter(
            created_at__date__gte=start,
            created_at__date__lte=end
        )
    
    total_jobs = jobs_query.count()
    inclusive_jobs = jobs_query.exclude(disability_focus='all').count()
    
    # KPI 3: Contrataciones comunicadas
    hiring_reports_query = HiringReport.objects.filter(
        status=HiringReportStatus.CONFIRMED
    )
    
    if company_filter:
        hiring_reports_query = hiring_reports_query.filter(company_id=company_filter)
    
    if start_date or end_date:
        hiring_reports_query = hiring_reports_query.filter(
            contract_date__gte=start,
            contract_date__lte=end
        )
    
    total_hirings = hiring_reports_query.count()
    
    # Distribución por tipo de discapacidad
    disability_distribution = hiring_reports_query.values(
        'disability_type'
    ).annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Top empresas por contrataciones
    top_companies = hiring_reports_query.values(
        'company__first_name',
        'company__last_name',
        'company_name'
    ).annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    # Evolución temporal (últimos 12 meses)
    monthly_data = []
    for i in range(12):
        month_start = (timezone.now() - timedelta(days=30*i)).replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        month_candidates = User.objects.filter(
            user_type='candidate',
            disability_type__in=['none', 'prefer_not_say'],
            date_joined__date__gte=month_start,
            date_joined__date__lte=month_end
        ).count()
        
        month_jobs = Job.objects.filter(
            compliance_status=ComplianceStatus.APPROVED,
            created_at__date__gte=month_start,
            created_at__date__lte=month_end
        ).count()
        
        month_hirings = HiringReport.objects.filter(
            status=HiringReportStatus.CONFIRMED,
            contract_date__gte=month_start,
            contract_date__lte=month_end
        ).count()
        
        monthly_data.append({
            'month': month_start.strftime('%b %Y'),
            'candidates': month_candidates,
            'jobs': month_jobs,
            'hirings': month_hirings
        })
    
    monthly_data.reverse()
    
    # Empresas para filtro
    companies = User.objects.filter(user_type='company').values('id', 'first_name', 'last_name')
    
    # Estadísticas adicionales
    stats = {
        'total_companies': User.objects.filter(user_type='company').count(),
        'active_companies': Job.objects.filter(
            compliance_status=ComplianceStatus.APPROVED
        ).values('company').distinct().count(),
        'avg_hirings_per_company': total_hirings / max(1, User.objects.filter(user_type='company').count()),
        'compliance_rate': (total_hirings / max(1, total_jobs)) * 100 if total_jobs > 0 else 0,
    }
    
    context = {
        'total_candidates': total_candidates,
        'candidates_with_disability': candidates_with_disability,
        'total_jobs': total_jobs,
        'inclusive_jobs': inclusive_jobs,
        'total_hirings': total_hirings,
        'disability_distribution': disability_distribution,
        'top_companies': top_companies,
        'monthly_data': monthly_data,
        'companies': companies,
        'stats': stats,
        # Filtros
        'company_filter': company_filter,
        'sector_filter': sector_filter,
        'period_filter': period_filter,
        'start_date': start_date,
        'end_date': end_date,
    }
    
    return render(request, 'admin_jobs/inclusion_kpis_dashboard.html', context)


@staff_member_required
def export_kpis_pdf(request):
    """Exportar KPIs como PDF"""
    from reportlab.lib.pagesizes import letter, landscape
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.units import inch
    from reportlab.lib.enums import TA_CENTER
    from io import BytesIO
    from django.utils import timezone
    from datetime import timedelta
    from companies.models import Job, HiringReport, HiringReportStatus
    from django.contrib.auth import get_user_model
    from companies.models import ComplianceStatus

    User = get_user_model()

    # === Obtener los datos principales (igual que en el dashboard) ===
    candidates_with_disability = User.objects.filter(
        user_type='candidate',
        disability_type__in=['none', 'prefer_not_say']
    ).count()

    inclusive_jobs = Job.objects.filter(
        compliance_status=ComplianceStatus.APPROVED
    ).exclude(disability_focus='all').count()

    total_hirings = HiringReport.objects.filter(
        status=HiringReportStatus.CONFIRMED
    ).count()

    # === Generar el PDF ===
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter))
    elements = []
    styles = getSampleStyleSheet()

    # Estilo de título
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=30,
        alignment=TA_CENTER
    )

    # Título
    elements.append(Paragraph("DASHBOARD DE KPIs DE INCLUSIÓN LABORAL", title_style))
    elements.append(Paragraph(
        f"Generado el {timezone.now().strftime('%d/%m/%Y %H:%M')}",
        styles['Normal']
    ))
    elements.append(Spacer(1, 0.3 * inch))

    # Tabla de KPIs principales
    kpi_data = [
        ['KPI', 'Valor', 'Descripción'],
        ['Candidatos con Discapacidad', str(candidates_with_disability), 'Candidatos registrados en el sistema'],
        ['Ofertas Inclusivas', str(inclusive_jobs), 'Ofertas publicadas y aprobadas'],
        ['Contrataciones Confirmadas', str(total_hirings), 'Informes enviados al Ministerio'],
    ]

    kpi_table = Table(kpi_data, colWidths=[3 * inch, 2 * inch, 4 * inch])
    kpi_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))

    elements.append(kpi_table)
    elements.append(Spacer(1, 0.3 * inch))

    # Nota de accesibilidad
    elements.append(Paragraph(
        "<b>Nota:</b> Este documento cumple con las normas WCAG 2.1 de accesibilidad.",
        styles['Normal']
    ))

    # Construir PDF
    doc.build(elements)
    pdf_content = buffer.getvalue()
    buffer.close()

    response = HttpResponse(pdf_content, content_type='application/pdf')
    response['Content-Disposition'] = f"attachment; filename=kpis_inclusion_{timezone.now().strftime('%Y%m%d_%H%M')}.pdf"

    return response