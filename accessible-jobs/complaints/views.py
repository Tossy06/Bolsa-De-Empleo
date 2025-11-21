# complaints/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q, Count
from django.core.paginator import Paginator
from .models import Complaint, ComplaintComment, ComplaintStatusHistory
from .forms import ComplaintForm, TrackComplaintForm, ComplaintCommentForm, ComplaintStatusUpdateForm


def get_client_ip(request):
    """Obtiene la IP del cliente"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def complaint_home_view(request):
    """
    Página principal del canal de denuncias
    """
    return render(request, 'complaints/home.html')


def file_complaint_view(request):
    """
    Formulario para presentar una denuncia
    """
    if request.method == 'POST':
        form = ComplaintForm(request.POST, request.FILES)
        if form.is_valid():
            complaint = form.save(commit=False)
            
            # Asociar usuario si está autenticado
            if request.user.is_authenticated:
                complaint.complainant_user = request.user
            
            # Capturar información de auditoría
            complaint.ip_address = get_client_ip(request)
            complaint.user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]
            
            complaint.save()
            
            # Enviar notificación a administradores
            send_admin_notification(complaint)
            
            # Mensaje de confirmación
            messages.success(
                request,
                f'Su denuncia ha sido recibida exitosamente. '
                f'Código de seguimiento: <strong>{complaint.tracking_code}</strong>. '
                f'Por favor guarde este código para consultar el estado de su denuncia.'
            )
            
            return redirect('complaints:confirmation', tracking_code=complaint.tracking_code)
    else:
        form = ComplaintForm()
    
    context = {
        'form': form,
    }
    return render(request, 'complaints/file_complaint.html', context)


def complaint_confirmation_view(request, tracking_code):
    """
    Página de confirmación después de presentar una denuncia
    """
    complaint = get_object_or_404(Complaint, tracking_code=tracking_code)
    
    context = {
        'complaint': complaint,
    }
    return render(request, 'complaints/confirmation.html', context)


def track_complaint_view(request):
    """
    Formulario para rastrear el estado de una denuncia
    """
    complaint = None
    
    if request.method == 'POST':
        form = TrackComplaintForm(request.POST)
        if form.is_valid():
            tracking_code = form.cleaned_data['tracking_code']
            return redirect('complaints:complaint_status', tracking_code=tracking_code)
    else:
        form = TrackComplaintForm()
    
    context = {
        'form': form,
    }
    return render(request, 'complaints/track_complaint.html', context)


def complaint_status_view(request, tracking_code):
    """
    Vista del estado de una denuncia
    """
    complaint = get_object_or_404(Complaint, tracking_code=tracking_code)
    
    # Historial de estados
    status_history = complaint.status_history.all()
    
    context = {
        'complaint': complaint,
        'status_history': status_history,
    }
    return render(request, 'complaints/complaint_status.html', context)


def send_admin_notification(complaint):
    """
    Envía notificación por email a los administradores
    """
    subject = f'Nueva denuncia recibida - {complaint.tracking_code}'
    message = f"""
    Se ha recibido una nueva denuncia en el sistema.
    
    Código de seguimiento: {complaint.tracking_code}
    Tipo: {complaint.get_complaint_type_display()}
    Asunto: {complaint.subject}
    Empresa: {complaint.company_name or 'No especificada'}
    
    Ingrese al panel de administración para revisar los detalles.
    """
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [settings.ADMIN_EMAIL],
            fail_silently=True,
        )
    except Exception as e:
        print(f"Error enviando email: {e}")


# ===== VISTAS PARA ADMINISTRADORES =====

def admin_required(view_func):
    """Decorador para verificar que el usuario sea admin"""
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
def admin_complaints_dashboard_view(request):
    """
    Dashboard de denuncias para administradores
    """
    # Estadísticas
    total_complaints = Complaint.objects.count()
    pending_complaints = Complaint.objects.filter(status='pending').count()
    under_review_complaints = Complaint.objects.filter(status='under_review').count()
    resolved_complaints = Complaint.objects.filter(status='resolved').count()
    
    # Denuncias por tipo
    complaints_by_type = Complaint.objects.values('complaint_type').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Denuncias recientes
    recent_complaints = Complaint.objects.all()[:10]
    
    # Denuncias pendientes de atención
    urgent_complaints = Complaint.objects.filter(
        status='pending',
        priority__gte=3
    ).order_by('-priority', 'created_at')[:5]
    
    context = {
        'total_complaints': total_complaints,
        'pending_complaints': pending_complaints,
        'under_review_complaints': under_review_complaints,
        'resolved_complaints': resolved_complaints,
        'complaints_by_type': complaints_by_type,
        'recent_complaints': recent_complaints,
        'urgent_complaints': urgent_complaints,
    }
    
    return render(request, 'complaints/admin_dashboard.html', context)


@login_required
@admin_required
def admin_complaints_list_view(request):
    """
    Lista de todas las denuncias para administradores
    """
    # Filtros
    status_filter = request.GET.get('status', '')
    priority_filter = request.GET.get('priority', '')
    search_query = request.GET.get('search', '')
    
    # Query base
    complaints = Complaint.objects.all()
    
    # Aplicar filtros
    if status_filter:
        complaints = complaints.filter(status=status_filter)
    
    if priority_filter:
        complaints = complaints.filter(priority=priority_filter)
    
    if search_query:
        complaints = complaints.filter(
            Q(tracking_code__icontains=search_query) |
            Q(subject__icontains=search_query) |
            Q(company_name__icontains=search_query)
        )
    
    # Ordenar
    complaints = complaints.order_by('-created_at')
    
    # Paginación
    paginator = Paginator(complaints, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'search_query': search_query,
    }
    
    return render(request, 'complaints/admin_list.html', context)


@login_required
@admin_required
def admin_complaint_detail_view(request, tracking_code):
    """
    Vista detallada de una denuncia para administradores
    """
    complaint = get_object_or_404(Complaint, tracking_code=tracking_code)
    
    # Formularios
    comment_form = ComplaintCommentForm()
    status_form = ComplaintStatusUpdateForm(instance=complaint)
    
    # Procesar actualización de estado
    if request.method == 'POST' and 'update_status' in request.POST:
        status_form = ComplaintStatusUpdateForm(request.POST, instance=complaint)
        if status_form.is_valid():
            old_status = complaint.status
            updated_complaint = status_form.save()
            
            # Guardar historial de cambio
            ComplaintStatusHistory.objects.create(
                complaint=complaint,
                previous_status=old_status,
                new_status=updated_complaint.status,
                changed_by=request.user,
                reason=status_form.cleaned_data.get('reason', '')
            )
            
            messages.success(request, 'Estado de la denuncia actualizado correctamente.')
            return redirect('complaints:admin_detail', tracking_code=tracking_code)
    
    # Procesar nuevo comentario
    if request.method == 'POST' and 'add_comment' in request.POST:
        comment_form = ComplaintCommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.complaint = complaint
            comment.author = request.user
            comment.save()
            
            messages.success(request, 'Comentario agregado correctamente.')
            return redirect('complaints:admin_detail', tracking_code=tracking_code)
    
    context = {
        'complaint': complaint,
        'comment_form': comment_form,
        'status_form': status_form,
        'comments': complaint.comments.all(),
        'status_history': complaint.status_history.all(),
    }
    
    return render(request, 'complaints/admin_detail.html', context)