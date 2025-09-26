
# companies/views.py (o jobs/views.py)
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Job
from .forms import JobForm

@login_required
def create_job_view(request):
    """Vista para crear una nueva oferta de trabajo"""
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.company = request.user
            job.save()
            messages.success(
                request, 
                f'¡Oferta "{job.title}" creada exitosamente! '
                f'{"Está destacada." if job.featured else "Ya está publicada."}'
            )
            return redirect('companies:dashboard')
        else:
            messages.error(
                request, 
                'Por favor corrige los errores en el formulario.'
            )
    else:
        form = JobForm()

    context = {
        'form': form,
        'title': 'Crear nueva oferta de trabajo'
    }
    return render(request, 'companies/create_job.html', context)

@login_required
def edit_job_view(request, job_id):
    """Vista para editar una oferta existente"""
    job = get_object_or_404(Job, id=job_id, company=request.user)
    
    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            job = form.save()
            messages.success(request, f'Oferta "{job.title}" actualizada correctamente.')
            return redirect('companies:dashboard')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = JobForm(instance=job)

    context = {
        'form': form,
        'job': job,
        'title': f'Editar: {job.title}'
    }
    return render(request, 'companies/create_job.html', context)

@login_required
def company_jobs_view(request):
    """Vista para ver todas las ofertas de la empresa"""
    jobs = Job.objects.filter(company=request.user).order_by('-created_at')
    
    # Filtros opcionales
    status_filter = request.GET.get('status', 'all')
    if status_filter == 'active':
        jobs = jobs.filter(is_active=True)
    elif status_filter == 'inactive':
        jobs = jobs.filter(is_active=False)
    elif status_filter == 'featured':
        jobs = jobs.filter(featured=True)

    search_query = request.GET.get('search', '')
    if search_query:
        jobs = jobs.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # Paginación
    paginator = Paginator(jobs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'search_query': search_query,
        'total_jobs': jobs.count(),
    }
    return render(request, 'companies/jobs_list.html', context)

@login_required
def toggle_job_status(request, job_id):
    """Vista para activar/desactivar una oferta"""
    job = get_object_or_404(Job, id=job_id, company=request.user)
    job.is_active = not job.is_active
    job.save()
    
    status = "activada" if job.is_active else "desactivada"
    messages.success(request, f'Oferta "{job.title}" {status} correctamente.')
    
    return redirect('companies:jobs_list')

def job_detail_view(request, job_id):
    """Vista pública para ver el detalle de una oferta"""
    job = get_object_or_404(Job, id=job_id, is_active=True)
    
    # Ofertas relacionadas (misma empresa o categoría)
    related_jobs = Job.objects.filter(
        is_active=True,
        disability_focus=job.disability_focus
    ).exclude(id=job.id)[:3]
    
    context = {
        'job': job,
        'related_jobs': related_jobs,
    }
    return render(request, 'jobs/job_detail.html', context)

# Ver aplicaciones recibidas
def applications_view(request):
    return HttpResponse("Aplicaciones recibidas")

# Ver notificaciones
def notifications_view(request):
    return HttpResponse("Notificaciones")

# Editar perfil de la empresa
def profile_view(request):
    return HttpResponse("Perfil de la empresa")
