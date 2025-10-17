
# companies/views.py (o jobs/views.py)
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Job
from .forms import JobForm

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from jobs.inclusive_language import InclusiveLanguageValidator

@login_required
def create_job_view(request):
    """Vista para crear una nueva oferta de trabajo"""
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.company = request.user
            job.save()
            
            # Registrar en auditoría
            from .models import AuditLog
            AuditLog.log_action(
                job=job,
                action='created',
                user=request.user,
                details={
                    'compliance_status': job.compliance_status,
                    'is_compliant': job.is_compliant(),
                },
                ip_address=request.META.get('REMOTE_ADDR'),
                notes='Oferta creada y marcada como pendiente de revisión'
            )
            
            messages.success(
                request, 
                f'✅ Oferta "{job.title}" creada exitosamente. '
                'Está pendiente de revisión por un administrador antes de publicarse.'
            )
            return redirect('core:dashboard')
        else:
            # 🔥 MOSTRAR ERRORES ESPECÍFICOS
            messages.error(
                request, 
                '❌ Por favor corrige los errores en el formulario.'
            )
            
            # Mostrar cada error específico
            for field, errors in form.errors.items():
                for error in errors:
                    if field == '__all__':
                        messages.error(request, f'Error: {error}')
                    else:
                        field_label = form.fields[field].label or field
                        messages.error(request, f'{field_label}: {error}')
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
            old_status = job.compliance_status  #GUARDAR ESTADO ANTERIOR
            job = form.save()
            
            #Registrar actualización
            from .models import AuditLog
            AuditLog.log_action(
                job=job,
                action='updated',
                user=request.user,
                details={
                    'old_status': old_status,
                    'new_status': job.compliance_status,
                },
                ip_address=request.META.get('REMOTE_ADDR'),
                notes='Oferta actualizada, requiere nueva revisión'
            )
            
            messages.success(request, f'Oferta "{job.title}" actualizada correctamente.')
            return redirect('core:dashboard')  # 🔧 Cambiar de 'companies:dashboard' a 'core:dashboard'
        else:
            messages.error(request, 'Corrige los errores en el formulario.')
    else:
        form = JobForm(instance=job)

    context = {
        'form': form,
        'job': job,
        'title': f'Editar: {job.title}'
    }
    return render(request, 'companies/create_job.html', context)

@login_required
def toggle_job_status(request, job_id):
    """Vista para activar/desactivar una oferta"""
    job = get_object_or_404(Job, id=job_id, company=request.user)
    job.is_active = not job.is_active
    job.save()
    
    status = "activada" if job.is_active else "desactivada"
    messages.success(request, f'Oferta "{job.title}" {status} correctamente.')
    
    return redirect('core:dashboard')

# Añadir esta función al final del archivo
@login_required
@require_http_methods(["POST"])
def validate_language_ajax(request):
    """Valida lenguaje en tiempo real"""
    text = request.POST.get('text', '')
    
    if not text:
        return JsonResponse({'valid': True, 'issues': []})
    
    issues = InclusiveLanguageValidator.scan_text(text)
    
    return JsonResponse({
        'valid': len(issues) == 0,
        'issues': issues
    })

