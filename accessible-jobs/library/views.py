# library/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Sum  # ← Agregar Sum
from django.http import FileResponse, Http404, JsonResponse
from django.core.paginator import Paginator
from .models import ResourceCategory, BestPracticeResource, ResourceBookmark


def company_required(view_func):
    """Decorador para verificar que el usuario sea empresa"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Debes iniciar sesión como empresa.')
            return redirect('accounts:login')
        
        if request.user.user_type != 'company':
            messages.error(request, 'Esta sección es solo para empresas.')
            return redirect('core:dashboard')
        
        return view_func(request, *args, **kwargs)
    return wrapper


@login_required
@company_required
def library_home_view(request):
    """
    Página principal de la biblioteca de mejores prácticas
    """
    # Categorías activas
    categories = ResourceCategory.objects.filter(is_active=True).annotate(
        resources_count=Count('resources', filter=Q(resources__is_published=True))
    )
    
    # Recursos destacados
    featured_resources = BestPracticeResource.objects.filter(
        is_published=True,
        is_featured=True
    ).select_related('category')[:6]
    
    # Recursos más vistos
    popular_resources = BestPracticeResource.objects.filter(
        is_published=True
    ).select_related('category').order_by('-view_count')[:5]
    
    # Recursos recientes
    recent_resources = BestPracticeResource.objects.filter(
        is_published=True
    ).select_related('category').order_by('-created_at')[:5]
    
    # Marcadores del usuario
    user_bookmarks_count = ResourceBookmark.objects.filter(user=request.user).count()
    
    context = {
        'categories': categories,
        'featured_resources': featured_resources,
        'popular_resources': popular_resources,
        'recent_resources': recent_resources,
        'user_bookmarks_count': user_bookmarks_count,
    }
    
    return render(request, 'library/home.html', context)


@login_required
@company_required
def resources_list_view(request):
    """
    Lista filtrable de recursos
    """
    # Filtros
    category_slug = request.GET.get('category', '')
    resource_type = request.GET.get('type', '')
    search_query = request.GET.get('search', '')
    sort_by = request.GET.get('sort', 'recent')  # recent, popular, title
    
    # Query base
    resources = BestPracticeResource.objects.filter(is_published=True).select_related('category')
    
    # Aplicar filtros
    if category_slug:
        resources = resources.filter(category__slug=category_slug)
    
    if resource_type:
        resources = resources.filter(resource_type=resource_type)
    
    if search_query:
        resources = resources.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(tags__icontains=search_query) |
            Q(author__icontains=search_query)
        )
    
    # Ordenamiento
    if sort_by == 'popular':
        resources = resources.order_by('-view_count', '-download_count')
    elif sort_by == 'title':
        resources = resources.order_by('title')
    else:  # recent
        resources = resources.order_by('-created_at')
    
    # Paginación
    paginator = Paginator(resources, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Obtener IDs de recursos marcados por el usuario
    bookmarked_ids = ResourceBookmark.objects.filter(
        user=request.user
    ).values_list('resource_id', flat=True)
    
    # Categorías para filtro
    categories = ResourceCategory.objects.filter(is_active=True)
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'bookmarked_ids': list(bookmarked_ids),
        'category_slug': category_slug,
        'resource_type': resource_type,
        'search_query': search_query,
        'sort_by': sort_by,
        'resource_type_choices': BestPracticeResource.RESOURCE_TYPE_CHOICES,
    }
    
    return render(request, 'library/resources_list.html', context)


@login_required
@company_required
def resource_detail_view(request, slug):
    """
    Vista detallada de un recurso
    """
    resource = get_object_or_404(
        BestPracticeResource,
        slug=slug,
        is_published=True
    )
    
    # Incrementar contador de vistas
    resource.increment_view_count()
    
    # Verificar si el usuario tiene este recurso marcado
    is_bookmarked = ResourceBookmark.objects.filter(
        user=request.user,
        resource=resource
    ).exists()
    
    # Recursos relacionados (misma categoría)
    related_resources = BestPracticeResource.objects.filter(
        category=resource.category,
        is_published=True
    ).exclude(id=resource.id).select_related('category')[:4]
    
    context = {
        'resource': resource,
        'is_bookmarked': is_bookmarked,
        'related_resources': related_resources,
    }
    
    return render(request, 'library/resource_detail.html', context)


@login_required
@company_required
def download_resource_view(request, slug):
    """
    Descargar archivo de recurso
    """
    resource = get_object_or_404(
        BestPracticeResource,
        slug=slug,
        is_published=True
    )
    
    if not resource.file:
        messages.error(request, 'Este recurso no tiene archivo disponible para descarga.')
        return redirect('library:resource_detail', slug=slug)
    
    # Incrementar contador de descargas
    resource.increment_download_count()
    
    try:
        response = FileResponse(resource.file.open('rb'), as_attachment=True)
        return response
    except Exception as e:
        messages.error(request, f'Error al descargar el archivo: {str(e)}')
        return redirect('library:resource_detail', slug=slug)


@login_required
@company_required
def toggle_bookmark_view(request, slug):
    """
    Añadir/remover marcador (AJAX)
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)
    
    resource = get_object_or_404(
        BestPracticeResource,
        slug=slug,
        is_published=True
    )
    
    bookmark, created = ResourceBookmark.objects.get_or_create(
        user=request.user,
        resource=resource
    )
    
    if not created:
        # Ya existía, eliminarlo
        bookmark.delete()
        return JsonResponse({
            'success': True,
            'bookmarked': False,
            'message': 'Marcador eliminado'
        })
    else:
        # Se creó nuevo marcador
        return JsonResponse({
            'success': True,
            'bookmarked': True,
            'message': 'Recurso guardado en marcadores'
        })


@login_required
@company_required
def my_bookmarks_view(request):
    """
    Lista de recursos marcados por el usuario
    """
    bookmarks = ResourceBookmark.objects.filter(
        user=request.user
    ).select_related('resource', 'resource__category').order_by('-created_at')
    
    # Paginación
    paginator = Paginator(bookmarks, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    
    return render(request, 'library/my_bookmarks.html', context)


@login_required
@company_required
def category_view(request, slug):
    """
    Vista de recursos por categoría
    """
    category = get_object_or_404(ResourceCategory, slug=slug, is_active=True)
    
    resources = BestPracticeResource.objects.filter(
        category=category,
        is_published=True
    ).select_related('category').order_by('-created_at')
    
    # Paginación
    paginator = Paginator(resources, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Obtener IDs de recursos marcados
    bookmarked_ids = ResourceBookmark.objects.filter(
        user=request.user
    ).values_list('resource_id', flat=True)
    
    context = {
        'category': category,
        'page_obj': page_obj,
        'bookmarked_ids': list(bookmarked_ids),
    }
    
    return render(request, 'library/category_detail.html', context)


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
def admin_library_stats_view(request):
    """
    Estadísticas de uso de la biblioteca (para administradores)
    """
    # Estadísticas generales
    total_resources = BestPracticeResource.objects.filter(is_published=True).count()
    total_categories = ResourceCategory.objects.filter(is_active=True).count()
    total_downloads = BestPracticeResource.objects.aggregate(
        total=Sum('download_count')
    )['total'] or 0
    total_views = BestPracticeResource.objects.aggregate(
        total=Sum('view_count')
    )['total'] or 0
    
    # Recursos más populares
    top_resources = BestPracticeResource.objects.filter(
        is_published=True
    ).order_by('-download_count')[:10]
    
    # Distribución por categoría
    category_stats = ResourceCategory.objects.filter(is_active=True).annotate(
        resources_count=Count('resources', filter=Q(resources__is_published=True)),
        total_views=Sum('resources__view_count'),
        total_downloads=Sum('resources__download_count')
    ).order_by('-resources_count')
    
    # Usuarios más activos (más marcadores)
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    active_users = User.objects.filter(
        user_type='company',
        resource_bookmarks__isnull=False
    ).annotate(
        bookmarks_count=Count('resource_bookmarks')
    ).order_by('-bookmarks_count')[:10]
    
    context = {
        'total_resources': total_resources,
        'total_categories': total_categories,
        'total_downloads': total_downloads,
        'total_views': total_views,
        'top_resources': top_resources,
        'category_stats': category_stats,
        'active_users': active_users,
    }
    
    return render(request, 'library/admin_stats.html', context)