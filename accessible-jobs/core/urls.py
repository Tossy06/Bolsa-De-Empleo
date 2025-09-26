from django.urls import path
from . import views

# Namespace para la navegación a las urls
app_name = 'core'

urlpatterns = [
    # ejemplo:
    path('', views.home_view, name='home'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('sobre-nosotros/', views.about_view, name='about'),
]
