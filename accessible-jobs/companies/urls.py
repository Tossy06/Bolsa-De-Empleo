from django.urls import path
from . import views

app_name = 'company'  # <- Muy importante

urlpatterns = [
    path('create-job/', views.create_job_view, name='create_job'),
    path('edit-job/<int:job_id>/', views.edit_job_view, name='edit_job'),
    path('toggle-job/<int:job_id>/', views.toggle_job_status, name='toggle_job'),
]