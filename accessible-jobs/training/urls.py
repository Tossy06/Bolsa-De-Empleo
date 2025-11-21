# training/urls.py
from django.urls import path
from . import views

app_name = 'training'

urlpatterns = [
    # Rutas para candidatos
    path('', views.courses_list_view, name='courses_list'),
    path('my-courses/', views.my_courses_view, name='my_courses'),
    path('course/<slug:slug>/', views.course_detail_view, name='course_detail'),
    path('course/<slug:slug>/enroll/', views.enroll_course_view, name='enroll_course'),
    path('course/<slug:slug>/lesson/<int:lesson_id>/', views.lesson_view, name='lesson_detail'),
    path('lesson/<int:lesson_id>/complete/', views.mark_lesson_complete, name='mark_lesson_complete'),
    path('certificate/<int:enrollment_id>/', views.certificate_view, name='certificate'),
    
    # Rutas para administradores
    path('admin/dashboard/', views.admin_training_dashboard, name='admin_dashboard'),
    path('admin/progress/', views.admin_candidate_progress_view, name='admin_candidate_progress'),
]