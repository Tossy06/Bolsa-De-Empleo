from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from .forms import AccessibleUserCreationForm, AccessibleLoginForm

@never_cache
@csrf_protect
def register_view(request):
    """
    Vista de registro de usuarios
    Incluye validación de formulario y hCaptcha
    """
    if request.user.is_authenticated:
        messages.info(request, 'Ya tienes una sesión activa.')
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        form = AccessibleUserCreationForm(request.POST)
        if form.is_valid():
            # Crear usuario pero no guardarlo aún
            user = form.save(commit=False)
            # Podemos añadir lógica adicional aquí
            user.save()
            
            # Iniciar sesión automáticamente después del registro
            login(request, user)
            
            # Mensaje de éxito accesible
            messages.success(
                request,
                f'¡Bienvenido {user.get_full_name()}! Tu cuenta ha sido creada exitosamente.'
            )
            
            return redirect('core:dashboard')
        else:
            # Mensaje de error accesible
            messages.error(
                request,
                'Por favor corrige los errores en el formulario. '
                'Los campos con error están marcados en rojo.'
            )
    else:
        form = AccessibleUserCreationForm()
    
    context = {
        'form': form,
        'title': 'Registro de Usuario',
        'page_description': 'Crea tu cuenta en nuestra plataforma de empleo inclusiva'
    }
    
    return render(request, 'accounts/register.html', context)


@never_cache
@csrf_protect
def login_view(request):
    """
    Vista de inicio de sesión
    Soporta "recordarme" para sesiones persistentes
    """
    if request.user.is_authenticated:
        messages.info(request, 'Ya tienes una sesión activa.')
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        form = AccessibleLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            remember_me = form.cleaned_data.get('remember_me')
            
            # Autenticar usuario
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                
                # Configurar duración de la sesión
                if not remember_me:
                    # Sesión expira al cerrar el navegador
                    request.session.set_expiry(0)
                else:
                    # Sesión dura 2 semanas
                    request.session.set_expiry(1209600)
                
                # Mensaje de bienvenida
                messages.success(
                    request,
                    f'¡Bienvenido de nuevo, {user.get_full_name()}!'
                )
                
                # Redirigir a la página solicitada o al dashboard
                next_url = request.GET.get('next', 'core:dashboard')
                return redirect(next_url)
        else:
            messages.error(
                request,
                'Usuario o contraseña incorrectos. Por favor intenta de nuevo.'
            )
    else:
        form = AccessibleLoginForm()
    
    context = {
        'form': form,
        'title': 'Iniciar Sesión',
        'page_description': 'Accede a tu cuenta'
    }
    
    return render(request, 'accounts/login.html', context)


@login_required
def logout_view(request):
    """
    Vista de cierre de sesión
    Requiere método POST por seguridad
    """
    if request.method == 'POST':
        username = request.user.get_full_name()
        logout(request)
        messages.success(
            request,
            f'Hasta pronto, {username}. Tu sesión ha sido cerrada correctamente.'
        )
        return redirect('core:home')
    
    return redirect('core:dashboard')