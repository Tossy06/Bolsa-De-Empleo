from django.urls import path
from . import views

app_name = 'company'  # <- Muy importante

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('create-job/', views.create_job_view, name='create_job'),
    path('applications/', views.applications_view, name='applications'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('profile/', views.profile_view, name='profile'),
]
