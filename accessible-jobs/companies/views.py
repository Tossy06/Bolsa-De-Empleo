from django.http import HttpResponse

# Panel principal de la empresa
def dashboard_view(request):
    return HttpResponse("Dashboard de la empresa")

# Crear oferta de trabajo
def create_job_view(request):
    return HttpResponse("Crear oferta de trabajo")

# Ver aplicaciones recibidas
def applications_view(request):
    return HttpResponse("Aplicaciones recibidas")

# Ver notificaciones
def notifications_view(request):
    return HttpResponse("Notificaciones")

# Editar perfil de la empresa
def profile_view(request):
    return HttpResponse("Perfil de la empresa")
