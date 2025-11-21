# messaging/urls.py
from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    # Bandeja de entrada
    path('', views.inbox_view, name='inbox'),
    
    # Iniciar conversación
    path('nueva/', views.start_conversation_view, name='start_conversation'),
    
    # Detalle de conversación
    path('conversacion/<int:pk>/', views.conversation_detail_view, name='conversation_detail'),
    
    # Archivar conversación
    path('conversacion/<int:pk>/archivar/', views.archive_conversation_view, name='archive_conversation'),
    
    # Notificaciones
    path('notificaciones/', views.notifications_view, name='notifications'),
]