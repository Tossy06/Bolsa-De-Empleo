# training/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.utils import timezone
from django.db.models import Count, Avg, Q
from .models import SocialSkillsCourse, CourseEnrollment, LessonProgress, CourseLesson


def candidate_required(view_func):
    """Decorador para verificar que el usuario sea candidato"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Debes iniciar sesión como candidato.')
            return redirect('accounts:login')
        
        if request.user.user_type != 'candidate':
            messages.error(request, 'Esta sección es solo para candidatos.')
            return redirect('core:dashboard')
        
        return view_func(request, *args, **kwargs)
    return wrapper


@login_required
@candidate_required
def courses_list_view(request):
    """
    Lista de cursos disponibles para candidatos
    """
    # Filtros
    category_filter = request.GET.get('category', '')
    difficulty_filter = request.GET.get('difficulty', '')
    search_query = request.GET.get('search', '')
    
    # Query base
    courses = SocialSkillsCourse.objects.filter(is_active=True)
    
    # Aplicar filtros
    if category_filter:
        courses = courses.filter(category=category_filter)
    
    if difficulty_filter:
        courses = courses.filter(difficulty=difficulty_filter)
    
    if search_query:
        courses = courses.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Anotar con número de lecciones e inscritos
    courses = courses.annotate(
        total_lessons=Count('lessons'),
        enrolled_count=Count('enrollments', filter=Q(enrollments__status='enrolled'))
    )
    
    # Obtener inscripciones del usuario actual
    user_enrollments = CourseEnrollment.objects.filter(
        candidate=request.user
    ).values_list('course_id', flat=True)
    
    context = {
        'courses': courses,
        'user_enrollments': list(user_enrollments),
        'category_filter': category_filter,
        'difficulty_filter': difficulty_filter,
        'search_query': search_query,
        'category_choices': SocialSkillsCourse.CATEGORY_CHOICES,
        'difficulty_choices': SocialSkillsCourse.DIFFICULTY_CHOICES,
    }
    
    return render(request, 'training/courses_list.html', context)


@login_required
@candidate_required
def course_detail_view(request, slug):
    """
    Vista detallada de un curso específico
    """
    course = get_object_or_404(SocialSkillsCourse, slug=slug, is_active=True)
    
    # Verificar si el usuario está inscrito
    enrollment = CourseEnrollment.objects.filter(
        candidate=request.user,
        course=course
    ).first()
    
    # Obtener lecciones
    lessons = course.lessons.all()
    
    # Si está inscrito, obtener progreso de lecciones
    lesson_progress = {}
    if enrollment:
        progress_records = LessonProgress.objects.filter(
            enrollment=enrollment
        ).select_related('lesson')
        
        lesson_progress = {
            progress.lesson_id: progress.completed
            for progress in progress_records
        }
    
    context = {
        'course': course,
        'lessons': lessons,
        'enrollment': enrollment,
        'lesson_progress': lesson_progress,
        'is_enrolled': enrollment is not None,
    }
    
    return render(request, 'training/course_detail.html', context)


@login_required
@candidate_required
def enroll_course_view(request, slug):
    """
    Inscribir al candidato en un curso
    """
    if request.method != 'POST':
        return HttpResponseForbidden("Método no permitido")
    
    course = get_object_or_404(SocialSkillsCourse, slug=slug, is_active=True)
    
    # Verificar si ya está inscrito
    enrollment, created = CourseEnrollment.objects.get_or_create(
        candidate=request.user,
        course=course,
        defaults={'status': 'enrolled'}
    )
    
    if created:
        messages.success(
            request,
            f'✅ Te has inscrito exitosamente en "{course.title}". ¡Comienza a aprender!'
        )
    else:
        messages.info(
            request,
            f'Ya estás inscrito en "{course.title}".'
        )
    
    return redirect('training:course_detail', slug=course.slug)


@login_required
@candidate_required
def lesson_view(request, slug, lesson_id):
    """
    Vista de una lección específica
    """
    course = get_object_or_404(SocialSkillsCourse, slug=slug, is_active=True)
    lesson = get_object_or_404(CourseLesson, id=lesson_id, course=course)
    
    # Verificar inscripción
    enrollment = get_object_or_404(
        CourseEnrollment,
        candidate=request.user,
        course=course
    )
    
    # Obtener o crear progreso de la lección
    lesson_progress, created = LessonProgress.objects.get_or_create(
        enrollment=enrollment,
        lesson=lesson
    )
    
    # Obtener todas las lecciones para navegación
    all_lessons = course.lessons.all()
    
    # Obtener progreso de todas las lecciones
    all_progress = LessonProgress.objects.filter(
        enrollment=enrollment
    ).values_list('lesson_id', 'completed')
    
    progress_dict = dict(all_progress)
    
    context = {
        'course': course,
        'lesson': lesson,
        'enrollment': enrollment,
        'lesson_progress': lesson_progress,
        'all_lessons': all_lessons,
        'progress_dict': progress_dict,
    }
    
    return render(request, 'training/lesson_detail.html', context)


@login_required
@candidate_required
def mark_lesson_complete(request, lesson_id):
    """
    Marcar una lección como completada (AJAX)
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)
    
    lesson = get_object_or_404(CourseLesson, id=lesson_id)
    
    # Verificar inscripción
    try:
        enrollment = CourseEnrollment.objects.get(
            candidate=request.user,
            course=lesson.course
        )
    except CourseEnrollment.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'No estás inscrito en este curso'
        }, status=403)
    
    # Obtener o crear progreso
    lesson_progress, created = LessonProgress.objects.get_or_create(
        enrollment=enrollment,
        lesson=lesson
    )
    
    # Marcar como completada
    lesson_progress.mark_as_completed()
    
    # Recalcular progreso del curso
    course_progress = enrollment.calculate_progress()
    
    return JsonResponse({
        'success': True,
        'lesson_completed': lesson_progress.completed,
        'course_progress': float(course_progress),
        'certificate_issued': enrollment.certificate_issued,
        'certificate_number': enrollment.certificate_number
    })


@login_required
@candidate_required
def my_courses_view(request):
    """
    Vista de cursos del candidato (mis cursos)
    """
    enrollments = CourseEnrollment.objects.filter(
        candidate=request.user
    ).select_related('course').order_by('-last_accessed_at')
    
    # Estadísticas
    stats = {
        'total': enrollments.count(),
        'in_progress': enrollments.filter(status='in_progress').count(),
        'completed': enrollments.filter(status='completed').count(),
        'certificates': enrollments.filter(certificate_issued=True).count(),
    }
    
    context = {
        'enrollments': enrollments,
        'stats': stats,
    }
    
    return render(request, 'training/my_courses.html', context)


@login_required
@candidate_required
def certificate_view(request, enrollment_id):
    """
    Vista del certificado de finalización
    """
    enrollment = get_object_or_404(
        CourseEnrollment,
        id=enrollment_id,
        candidate=request.user,
        certificate_issued=True
    )
    
    context = {
        'enrollment': enrollment,
    }
    
    return render(request, 'training/certificate.html', context)


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
def admin_training_dashboard(request):
    """
    Dashboard de formación para administradores
    """
    # Estadísticas generales
    total_courses = SocialSkillsCourse.objects.count()
    active_courses = SocialSkillsCourse.objects.filter(is_active=True).count()
    total_enrollments = CourseEnrollment.objects.count()
    total_completed = CourseEnrollment.objects.filter(status='completed').count()
    total_certificates = CourseEnrollment.objects.filter(certificate_issued=True).count()
    
    # Cursos más populares
    popular_courses = SocialSkillsCourse.objects.annotate(
        enrollment_count=Count('enrollments')
    ).order_by('-enrollment_count')[:5]
    
    # Tasa de finalización por curso con PORCENTAJE CALCULADO
    completion_stats = SocialSkillsCourse.objects.annotate(
        total_enrollments=Count('enrollments'),
        completed_enrollments=Count('enrollments', filter=Q(enrollments__status='completed'))
    ).filter(total_enrollments__gt=0)
    
    # ✅ CALCULAR PORCENTAJE EN PYTHON
    completion_stats_with_percentage = []
    for course in completion_stats:
        percentage = (course.completed_enrollments / course.total_enrollments * 100) if course.total_enrollments > 0 else 0
        completion_stats_with_percentage.append({
            'title': course.title,
            'total_enrollments': course.total_enrollments,
            'completed_enrollments': course.completed_enrollments,
            'completion_percentage': round(percentage, 1)
        })
    
    # Actividad reciente
    recent_enrollments = CourseEnrollment.objects.select_related(
        'candidate', 'course'
    ).order_by('-enrolled_at')[:10]
    
    recent_completions = CourseEnrollment.objects.filter(
        status='completed'
    ).select_related('candidate', 'course').order_by('-completed_at')[:10]
    
    context = {
        'total_courses': total_courses,
        'active_courses': active_courses,
        'total_enrollments': total_enrollments,
        'total_completed': total_completed,
        'total_certificates': total_certificates,
        'popular_courses': popular_courses,
        'completion_stats': completion_stats_with_percentage,  # ✅ USAR LA NUEVA LISTA
        'recent_enrollments': recent_enrollments,
        'recent_completions': recent_completions,
    }
    
    return render(request, 'training/admin_dashboard.html', context)


@login_required
@admin_required
def admin_candidate_progress_view(request):
    """
    Ver progreso de todos los candidatos
    """
    # Filtros
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    
    # Query base
    enrollments = CourseEnrollment.objects.select_related(
        'candidate', 'course'
    ).order_by('-last_accessed_at')
    
    # Aplicar filtros
    if search_query:
        enrollments = enrollments.filter(
            Q(candidate__first_name__icontains=search_query) |
            Q(candidate__last_name__icontains=search_query) |
            Q(candidate__email__icontains=search_query) |
            Q(course__title__icontains=search_query)
        )
    
    if status_filter:
        enrollments = enrollments.filter(status=status_filter)
    
    context = {
        'enrollments': enrollments,
        'search_query': search_query,
        'status_filter': status_filter,
        'status_choices': CourseEnrollment.STATUS_CHOICES,
    }
    
    return render(request, 'training/admin_candidate_progress.html', context)