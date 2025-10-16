# jobs/views.py
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from companies.models import Job, ComplianceStatus
from django.contrib.auth.decorators import login_required


def job_list_view(request):
    """
    Lista pública de ofertas aprobadas
    Accesible para todos (candidatos y visitantes)
    """
    # Filtros
    search_query = request.GET.get('search', '')
    location = request.GET.get('location', '')
    job_type = request.GET.get('job_type', '')
    disability_focus = request.GET.get('disability_focus', '')
    
    # Query base: solo ofertas aprobadas y activas
    jobs = Job.objects.filter(
        compliance_status=ComplianceStatus.APPROVED,
        is_active=True
    ).select_related('company').order_by('-created_at')
    
    # Aplicar filtros
    if search_query:
        jobs = jobs.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(requirements__icontains=search_query)
        )
    
    if location:
        jobs = jobs.filter(location__icontains=location)
    
    if job_type:
        jobs = jobs.filter(job_type=job_type)
    
    if disability_focus:
        jobs = jobs.filter(disability_focus=disability_focus)
    
    # Paginación
    paginator = Paginator(jobs, 12)  # 12 ofertas por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'location': location,
        'job_type': job_type,
        'disability_focus': disability_focus,
        'total_jobs': jobs.count(),
    }
    
    return render(request, 'jobs/job_list.html', context)


def job_detail_view(request, job_id):
    """
    Vista detallada de una oferta
    Accesible para todos
    """
    job = get_object_or_404(
        Job,
        id=job_id,
        compliance_status=ComplianceStatus.APPROVED,
        is_active=True
    )
    
    # Ofertas relacionadas de la misma empresa
    related_jobs = Job.objects.filter(
        company=job.company,
        compliance_status=ComplianceStatus.APPROVED,
        is_active=True
    ).exclude(id=job_id)[:3]
    
    context = {
        'job': job,
        'related_jobs': related_jobs,
    }
    
    return render(request, 'jobs/job_detail.html', context)


@login_required
def my_applications_view(request):
    """
    Mis postulaciones (solo para candidatos)
    """
    if request.user.user_type != 'candidate':
        from django.contrib import messages
        from django.shortcuts import redirect
        messages.error(request, 'Esta sección es solo para candidatos.')
        return redirect('core:dashboard')
    
    # TODO: Implementar cuando tenga el modelo de Application
    context = {
        'applications': [],  # Placeholder
    }
    
    return render(request, 'jobs/my_applications.html', context)