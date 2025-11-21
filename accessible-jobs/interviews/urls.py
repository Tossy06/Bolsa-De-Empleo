# interviews/urls.py
from django.urls import path
from . import views

app_name = 'interviews'

urlpatterns = [
    # Lista de entrevistas
    path('', views.interviews_list_view, name='list'),
    
    # Programar nueva entrevista
    path('programar/', views.schedule_interview_view, name='schedule'),
    
    # Detalle de entrevista
    path('<uuid:pk>/', views.interview_detail_view, name='detail'),
    
    # Confirmar entrevista
    path('<uuid:pk>/confirmar/', views.confirm_interview_view, name='confirm'),
    
    # Cancelar entrevista
    path('<uuid:pk>/cancelar/', views.cancel_interview_view, name='cancel'),
    
    # Reprogramar entrevista
    path('<uuid:pk>/reprogramar/', views.reschedule_interview_view, name='reschedule'),
]