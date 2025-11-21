# core/views.py
from django.shortcuts import render
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
    user = request.user
    
    # Contexto base
    context = {
        'title': 'Mi Panel',
        'page_description': f'Panel de control de {user.get_full_name()}',
        'user': user,
    }
    
    # Dashboard según tipo de usuario
    if user.user_type == 'candidate':
        from training.models import CourseEnrollment  # ← AGREGAR
        
        recommended_jobs = Job.objects.filter(
            compliance_status=ComplianceStatus.APPROVED,
            is_active=True
        ).select_related('company').order_by('-created_at')[:5]
        
        # ← AGREGAR ESTADÍSTICAS DE CURSOS
        my_courses = CourseEnrollment.objects.filter(candidate=user)
        
        context.update({
            'recommended_jobs': recommended_jobs,
            'total_courses_enrolled': my_courses.count(),
            'courses_in_progress': my_courses.filter(status='in_progress').count(),
            'courses_completed': my_courses.filter(status='completed').count(),
            'certificates_earned': my_courses.filter(certificate_issued=True).count(),
        })
        
        return render(request, 'core/dashboard_candidate.html', context)
    
    elif user.user_type == 'company':
        jobs = Job.objects.filter(company=user).order_by('-created_at')
        
        # AGREGAR ESTADÍSTICAS PARA EMPRESAS
        context.update({
            'jobs': jobs,
            'total_jobs': jobs.count(),
            'active_jobs': jobs.filter(is_active=True).count(),
            'pending_jobs': jobs.filter(compliance_status=ComplianceStatus.PENDING_REVIEW).count(),
            'approved_jobs': jobs.filter(compliance_status=ComplianceStatus.APPROVED).count(),
            'rejected_jobs': jobs.filter(compliance_status=ComplianceStatus.REJECTED).count(),
        })
        return render(request, 'core/dashboard_company.html', context)
    
    else:  # admin
        # ESTADÍSTICAS PARA ADMIN
        context.update({
            'total_users': User.objects.count(),
            'total_companies': User.objects.filter(user_type='company').count(),
            'total_candidates': User.objects.filter(user_type='candidate').count(),
            'total_jobs': Job.objects.count(),
            'pending_jobs': Job.objects.filter(compliance_status=ComplianceStatus.PENDING_REVIEW).count(),
            'approved_jobs': Job.objects.filter(compliance_status=ComplianceStatus.APPROVED).count(),
            'rejected_jobs': Job.objects.filter(compliance_status=ComplianceStatus.REJECTED).count(),
        })
        return render(request, 'core/dashboard_admin.html', context)


def about_view(request):
    context = {
        'title': 'Sobre Nosotros',
        'page_description': 'Conoce más sobre nuestra misión de inclusión laboral'
    }
    return render(request, 'core/about.html', context)