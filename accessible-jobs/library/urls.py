# library/urls.py
from django.urls import path
from . import views

app_name = 'library'

urlpatterns = [
    # Rutas para empresas
    path('', views.library_home_view, name='home'),
    path('recursos/', views.resources_list_view, name='resources_list'),
    path('recurso/<slug:slug>/', views.resource_detail_view, name='resource_detail'),
    path('recurso/<slug:slug>/descargar/', views.download_resource_view, name='download_resource'),
    path('recurso/<slug:slug>/marcar/', views.toggle_bookmark_view, name='toggle_bookmark'),
    path('mis-marcadores/', views.my_bookmarks_view, name='my_bookmarks'),
    path('categoria/<slug:slug>/', views.category_view, name='category_detail'),
    
    # Rutas para administradores
    path('admin/estadisticas/', views.admin_library_stats_view, name='admin_stats'),
]