"""
Vistas principales de la aplicación
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

def home_view(request):
    """
    Página de inicio - Landing page
    Accesible para todos los usuarios
    """
    context = {
        'title': 'Inicio',
        'page_description': 'Plataforma de empleo inclusiva para personas con discapacidad'
    }
    return render(request, 'core/home.html', context)


@login_required
def dashboard_view(request):
    """
    Dashboard principal del usuario
    Muestra contenido personalizado según el tipo de usuario
    """
    user = request.user
    
    context = {
        'title': 'Mi Panel',
        'page_description': f'Panel de control de {user.get_full_name()}',
        'user': user,
    }
    
    # Renderizar template diferente según tipo de usuario
    if user.user_type == 'candidate':
        return render(request, 'core/dashboard_candidate.html', context)
    elif user.user_type == 'company':
        return render(request, 'core/dashboard_company.html', context)
    else:
        return render(request, 'core/dashboard_admin.html', context)


def about_view(request):
    """
    Página sobre nosotros
    """
    context = {
        'title': 'Sobre Nosotros',
        'page_description': 'Conoce más sobre nuestra misión de inclusión laboral'
    }
    return render(request, 'core/about.html', context)