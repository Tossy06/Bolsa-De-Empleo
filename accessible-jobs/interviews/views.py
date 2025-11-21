# interviews/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from .models import Interview, InterviewRescheduleRequest, InterviewNotification
from .forms import (
    ScheduleInterviewForm, ConfirmInterviewForm, CancelInterviewForm,
    RescheduleInterviewForm, InterviewFeedbackForm, InterviewSearchForm
)


@login_required
def interviews_list_view(request):
    """
    Lista de entrevistas según el tipo de usuario
    """
    user = request.user
    
    # Obtener entrevistas según tipo de usuario
    if user.user_type == 'company':
        interviews = Interview.objects.filter(company=user)
    elif user.user_type == 'candidate':
        interviews = Interview.objects.filter(candidate=user)
    else:
        interviews = Interview.objects.none()
    
    # Filtros
    search_form = InterviewSearchForm(request.GET)
    if search_form.is_valid():
        search_query = search_form.cleaned_data.get('search', '')
        status_filter = search_form.cleaned_data.get('status', '')
        date_from = search_form.cleaned_data.get('date_from')
        date_to = search_form.cleaned_data.get('date_to')
        
        if search_query:
            interviews = interviews.filter(
                Q(title__icontains=search_query) |
                Q(job_title__icontains=search_query) |
                Q(candidate__first_name__icontains=search_query) |
                Q(candidate__last_name__icontains=search_query) |
                Q(company__first_name__icontains=search_query) |
                Q(company__last_name__icontains=search_query)
            )
        
        if status_filter:
            interviews = interviews.filter(status=status_filter)
        
        if date_from:
            interviews = interviews.filter(scheduled_date__gte=date_from)
        
        if date_to:
            interviews = interviews.filter(scheduled_date__lte=date_to)
    
    # Ordenar
    interviews = interviews.select_related('candidate', 'company').order_by('-scheduled_date', '-scheduled_time')
    
    # Separar por estado
    upcoming_interviews = interviews.filter(
        status__in=['proposed', 'confirmed'],
        scheduled_date__gte=timezone.now().date()
    )
    past_interviews = interviews.filter(
        Q(scheduled_date__lt=timezone.now().date()) |
        Q(status__in=['completed', 'cancelled'])
    )
    
    # Paginación
    paginator = Paginator(interviews, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_form': search_form,
        'upcoming_interviews': upcoming_interviews[:5],
        'past_interviews': past_interviews[:5],
        'total_interviews': interviews.count(),
        'upcoming_count': upcoming_interviews.count(),
    }
    
    return render(request, 'interviews/list.html', context)


@login_required
def schedule_interview_view(request):
    """
    Programar una nueva entrevista (solo empresas)
    """
    if request.user.user_type != 'company':
        messages.error(request, 'Solo las empresas pueden programar entrevistas.')
        return redirect('interviews:list')
    
    if request.method == 'POST':
        form = ScheduleInterviewForm(request.POST, company=request.user)
        if form.is_valid():
            interview = form.save(commit=False)
            interview.company = request.user
            interview.company_confirmed = True
            interview.save()
            
            # Enviar notificación
            send_interview_notification(interview, 'created')
            
            messages.success(request, 'Entrevista programada exitosamente.')
            return redirect('interviews:detail', pk=interview.pk)
    else:
        form = ScheduleInterviewForm(company=request.user)
    
    context = {
        'form': form,
    }
    
    return render(request, 'interviews/schedule.html', context)


@login_required
def interview_detail_view(request, pk):
    """
    Vista detallada de una entrevista
    """
    interview = get_object_or_404(Interview, pk=pk)
    
    # Verificar permisos
    if request.user not in [interview.candidate, interview.company]:
        messages.error(request, 'No tienes permiso para ver esta entrevista.')
        return redirect('interviews:list')
    
    # Obtener solicitudes de reprogramación
    reschedule_requests = interview.reschedule_requests.all().order_by('-created_at')
    
    context = {
        'interview': interview,
        'reschedule_requests': reschedule_requests,
        'can_confirm': request.user == interview.candidate and not interview.candidate_confirmed,
        'can_cancel': interview.can_be_cancelled(),
        'can_reschedule': interview.can_be_cancelled(),
    }
    
    return render(request, 'interviews/detail.html', context)


@login_required
def confirm_interview_view(request, pk):
    """
    Confirmar asistencia a entrevista (candidato)
    """
    interview = get_object_or_404(Interview, pk=pk)
    
    # Verificar permisos
    if request.user != interview.candidate:
        messages.error(request, 'Solo el candidato puede confirmar esta entrevista.')
        return redirect('interviews:detail', pk=pk)
    
    if interview.candidate_confirmed:
        messages.info(request, 'Ya has confirmado esta entrevista.')
        return redirect('interviews:detail', pk=pk)
    
    if request.method == 'POST':
        form = ConfirmInterviewForm(request.POST)
        if form.is_valid():
            interview.confirm_by_candidate()
            
            # Enviar notificación
            send_interview_notification(interview, 'confirmed')
            
            messages.success(request, '¡Has confirmado tu asistencia a la entrevista!')
            return redirect('interviews:detail', pk=pk)
    else:
        form = ConfirmInterviewForm()
    
    context = {
        'interview': interview,
        'form': form,
    }
    
    return render(request, 'interviews/confirm.html', context)


@login_required
def cancel_interview_view(request, pk):
    """
    Cancelar una entrevista
    """
    interview = get_object_or_404(Interview, pk=pk)
    
    # Verificar permisos
    if request.user not in [interview.candidate, interview.company]:
        messages.error(request, 'No tienes permiso para cancelar esta entrevista.')
        return redirect('interviews:detail', pk=pk)
    
    if not interview.can_be_cancelled():
        messages.error(request, 'Esta entrevista no puede ser cancelada.')
        return redirect('interviews:detail', pk=pk)
    
    if request.method == 'POST':
        form = CancelInterviewForm(request.POST)
        if form.is_valid():
            reason = form.cleaned_data['reason']
            interview.cancel(request.user, reason)
            
            # Enviar notificación
            send_interview_notification(interview, 'cancelled')
            
            messages.success(request, 'La entrevista ha sido cancelada.')
            return redirect('interviews:detail', pk=pk)
    else:
        form = CancelInterviewForm()
    
    context = {
        'interview': interview,
        'form': form,
    }
    
    return render(request, 'interviews/cancel.html', context)


@login_required
def reschedule_interview_view(request, pk):
    """
    Solicitar reprogramación de entrevista
    """
    interview = get_object_or_404(Interview, pk=pk)
    
    # Verificar permisos
    if request.user not in [interview.candidate, interview.company]:
        messages.error(request, 'No tienes permiso para reprogramar esta entrevista.')
        return redirect('interviews:detail', pk=pk)
    
    if not interview.can_be_cancelled():
        messages.error(request, 'Esta entrevista no puede ser reprogramada.')
        return redirect('interviews:detail', pk=pk)
    
    if request.method == 'POST':
        form = RescheduleInterviewForm(request.POST)
        if form.is_valid():
            reschedule_request = form.save(commit=False)
            reschedule_request.interview = interview
            reschedule_request.requested_by = request.user
            reschedule_request.save()
            
            # Enviar notificación
            send_interview_notification(interview, 'rescheduled')
            
            messages.success(request, 'Solicitud de reprogramación enviada.')
            return redirect('interviews:detail', pk=pk)
    else:
        form = RescheduleInterviewForm()
    
    context = {
        'interview': interview,
        'form': form,
    }
    
    return render(request, 'interviews/reschedule.html', context)


def send_interview_notification(interview, notification_type):
    """
    Envía notificaciones sobre la entrevista
    """
    # Determinar destinatarios
    if notification_type == 'created':
        recipients = [interview.candidate]
        message = f"Has sido invitado a una entrevista: {interview.title}"
    elif notification_type == 'confirmed':
        recipients = [interview.company]
        message = f"{interview.candidate.get_full_name()} ha confirmado la entrevista"
    elif notification_type == 'cancelled':
        if interview.cancelled_by == interview.candidate:
            recipients = [interview.company]
        else:
            recipients = [interview.candidate]
        message = f"La entrevista {interview.title} ha sido cancelada"
    elif notification_type == 'rescheduled':
        if interview.cancelled_by == interview.candidate:
            recipients = [interview.company]
        else:
            recipients = [interview.candidate]
        message = f"Se ha solicitado reprogramar la entrevista {interview.title}"
    else:
        recipients = []
        message = ""
    
    # Crear notificaciones
    for user in recipients:
        InterviewNotification.objects.create(
            user=user,
            interview=interview,
            notification_type=notification_type,
            message=message
        )
        
        # Enviar email
        try:
            send_mail(
                subject=f'Notificación de Entrevista - {interview.title}',
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True,
            )
        except Exception as e:
            print(f"Error enviando email: {e}")