"""
URLs para la aplicación de cuentas de usuario
Incluye registro, login, logout y gestión de perfil
"""

from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Autenticación básica
    path('registro/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Perfil de usuario (las crearemos después)
    # path('perfil/', views.profile_view, name='profile'),
    # path('perfil/editar/', views.edit_profile_view, name='edit_profile'),
    
    # Recuperación de contraseña (las crearemos después)
    # path('recuperar-password/', views.password_reset_view, name='password_reset'),
]