from django.urls import path
from . import views

app_name = 'company'  # <- Muy importante

urlpatterns = [
    #path('dashboard/', views.dashboard_view, name='dashboard'),  # <- Agregar esta línea
    path('create-job/', views.create_job_view, name='create_job'),
    path('edit-job/<int:job_id>/', views.edit_job_view, name='edit_job'),  # <- Agregar si quieres editar
    path('applications/', views.applications_view, name='applications'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('profile/', views.profile_view, name='profile'),
]