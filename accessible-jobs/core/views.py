# core/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from companies.models import Job, ComplianceStatus
from accounts.models import User

def home_view(request):
    context = {
        'title': 'Inicio',
        'page_description': 'Plataforma de empleo inclusiva para personas con discapacidad'
    }
    return render(request, 'core/home.html', context)


@login_required
def dashboard_view(request):
    """Vista principal del dashboard que redirige según el tipo de usuario"""
    user = request.user
    
    # Redirigir según tipo de usuario
    if user.user_type == 'candidate':
        return dashboard_candidate_view(request)
    elif user.user_type == 'company':
        return dashboard_company_view(request)
    elif user.is_staff or user.is_superuser:
        return dashboard_admin_view(request)
    else:
        return render(request, 'core/dashboard_default.html')


@login_required
def dashboard_candidate_view(request):
    """Dashboard para candidatos con mensajería y entrevistas"""
    from training.models import CourseEnrollment
    from messaging.models import Conversation
    from interviews.models import Interview
    from django.utils import timezone
    
    user = request.user
    
    # Datos de formación
    try:
        enrollments = CourseEnrollment.objects.filter(candidate=user)
        total_courses_enrolled = enrollments.count()
        courses_in_progress = enrollments.filter(status='in_progress').count()
        certificates_earned = enrollments.filter(certificate_issued=True).count()
    except Exception as e:
        print(f"Error en cursos: {e}")
        total_courses_enrolled = 0
        courses_in_progress = 0
        certificates_earned = 0
    
    # Datos de mensajería
    try:
        conversations = Conversation.objects.filter(
            candidate=user,
            is_archived_by_candidate=False
        ).select_related('company').order_by('-updated_at')[:5]
        
        all_conversations = Conversation.objects.filter(candidate=user)
        unread_messages_count = sum([
            conv.get_unread_count_for_candidate() 
            for conv in all_conversations
        ])
    except Exception as e:
        print(f"Error en mensajes: {e}")
        conversations = []
        unread_messages_count = 0
    
    # ✨ Datos de entrevistas
    try:
        upcoming_interviews = Interview.objects.filter(
            candidate=user,
            status__in=['proposed', 'confirmed'],
            scheduled_date__gte=timezone.now().date()
        ).select_related('company').order_by('scheduled_date', 'scheduled_time')[:5]
        
        upcoming_interviews_count = upcoming_interviews.count()
    except Exception as e:
        print(f"Error en entrevistas: {e}")
        upcoming_interviews = []
        upcoming_interviews_count = 0
    
    # Trabajos recomendados
    try:
        from companies.models import Job, ComplianceStatus
        recommended_jobs = Job.objects.filter(
            compliance_status=ComplianceStatus.APPROVED,
            is_active=True
        ).select_related('company').order_by('-created_at')[:5]
    except Exception as e:
        print(f"Error en trabajos: {e}")
        recommended_jobs = []
    
    context = {
        'title': 'Mi Panel',
        'page_description': f'Panel de control de {user.get_full_name()}',
        'user': user,
        'total_courses_enrolled': total_courses_enrolled,
        'courses_in_progress': courses_in_progress,
        'certificates_earned': certificates_earned,
        'recent_conversations': conversations,
        'unread_messages_count': unread_messages_count,
        'upcoming_interviews': upcoming_interviews,
        'upcoming_interviews_count': upcoming_interviews_count,
        'recommended_jobs': recommended_jobs,
    }
    
    return render(request, 'core/dashboard_candidate.html', context)


@login_required
def dashboard_company_view(request):
    """Dashboard para empresas con mensajería y entrevistas"""
    from messaging.models import Conversation
    from interviews.models import Interview
    from companies.models import Job
    from django.utils import timezone
    
    user = request.user
    
    # Datos de trabajos
    try:
        jobs = Job.objects.filter(company=user).order_by('-created_at')[:6]
        job_posts_count = Job.objects.filter(company=user).count()
        applications_count = 0
        job_views_count = 0
    except Exception as e:
        print(f"Error en trabajos: {e}")
        jobs = []
        job_posts_count = 0
        applications_count = 0
        job_views_count = 0
    
    # Datos de mensajería
    try:
        conversations = Conversation.objects.filter(
            company=user,
            is_archived_by_company=False
        ).select_related('candidate').order_by('-updated_at')[:5]
        
        all_conversations = Conversation.objects.filter(company=user)
        unread_messages_count = sum([
            conv.get_unread_count_for_company() 
            for conv in all_conversations
        ])
    except Exception as e:
        print(f"Error en mensajes: {e}")
        conversations = []
        unread_messages_count = 0
    
    # ✨ Datos de entrevistas
    try:
        upcoming_interviews = Interview.objects.filter(
            company=user,
            status__in=['proposed', 'confirmed'],
            scheduled_date__gte=timezone.now().date()
        ).select_related('candidate').order_by('scheduled_date', 'scheduled_time')[:5]
        
        upcoming_interviews_count = upcoming_interviews.count()
    except Exception as e:
        print(f"Error en entrevistas: {e}")
        upcoming_interviews = []
        upcoming_interviews_count = 0
    
    context = {
        'title': 'Mi Panel',
        'page_description': f'Panel de control de {user.get_full_name()}',
        'user': user,
        'recent_conversations': conversations,
        'unread_messages_count': unread_messages_count,
        'upcoming_interviews': upcoming_interviews,
        'upcoming_interviews_count': upcoming_interviews_count,
        'job_posts_count': job_posts_count,
        'applications_count': applications_count,
        'job_views_count': job_views_count,
        'jobs': jobs,
    }
    
    return render(request, 'core/dashboard_company.html', context)


@login_required
def dashboard_admin_view(request):
    """Dashboard para administradores"""
    user = request.user
    
    context = {
        'title': 'Panel de Administración',
        'page_description': 'Panel de control del administrador',
        'user': user,
        'total_users': User.objects.count(),
        'total_companies': User.objects.filter(user_type='company').count(),
        'total_candidates': User.objects.filter(user_type='candidate').count(),
        'total_jobs': Job.objects.count(),
        'pending_jobs': Job.objects.filter(compliance_status=ComplianceStatus.PENDING_REVIEW).count(),
        'approved_jobs': Job.objects.filter(compliance_status=ComplianceStatus.APPROVED).count(),
        'rejected_jobs': Job.objects.filter(compliance_status=ComplianceStatus.REJECTED).count(),
    }
    
    return render(request, 'core/dashboard_admin.html', context)


def about_view(request):
    context = {
        'title': 'Sobre Nosotros',
        'page_description': 'Conoce más sobre nuestra misión de inclusión laboral'
    }
    return render(request, 'core/about.html', context)