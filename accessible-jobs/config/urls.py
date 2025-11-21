"""
Configuración principal de URLs del proyecto
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/jobs/', include('admin_jobs.urls')),

    # Ofertas públicas
    path('empleos/', include('jobs.urls')),

    # URLs de la aplicación de cuentas
    path('cuentas/', include('accounts.urls')),

    # URLs de empresas
    path('company/', include('companies.urls')),

    # Panel de administración de Django
    path('admin/', admin.site.urls),

    # App de training
    path('training/', include('training.urls')),

    path('biblioteca/', include('library.urls')),

    # URLs de la aplicación core (home, dashboard, etc)
    path('', include('core.urls')),
    
    # URLs de trabajos (las crearemos después)
    # path('trabajos/', include('jobs.urls')),
]

# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Personalizar títulos del admin
admin.site.site_header = "Portal de Empleo Inclusivo - Administración"
admin.site.site_title = "Admin Portal"
admin.site.index_title = "Bienvenido al panel de administración"