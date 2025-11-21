# complaints/urls.py
from django.urls import path
from . import views

app_name = 'complaints'

urlpatterns = [
    # Rutas públicas
    path('', views.complaint_home_view, name='home'),
    path('presentar/', views.file_complaint_view, name='file_complaint'),
    path('confirmacion/<str:tracking_code>/', views.complaint_confirmation_view, name='confirmation'),
    path('rastrear/', views.track_complaint_view, name='track'),
    path('estado/<str:tracking_code>/', views.complaint_status_view, name='complaint_status'),
    
    # Rutas para administradores
    path('admin/dashboard/', views.admin_complaints_dashboard_view, name='admin_dashboard'),
    path('admin/lista/', views.admin_complaints_list_view, name='admin_list'),
    path('admin/detalle/<str:tracking_code>/', views.admin_complaint_detail_view, name='admin_detail'),
]