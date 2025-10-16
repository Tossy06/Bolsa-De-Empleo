# admin_jobs/urls.py
from django.urls import path
from . import views

app_name = 'admin_jobs'

urlpatterns = [
    path('pending/', views.pending_jobs_list, name='pending_list'),
    path('review/<int:job_id>/', views.review_job_detail, name='review_detail'),
    path('approve/<int:job_id>/', views.approve_job, name='approve'),
    path('reject/<int:job_id>/', views.reject_job, name='reject'),
    path('request-changes/<int:job_id>/', views.request_changes, name='request_changes'),
    path('audit-logs/', views.audit_logs_view, name='audit_logs'),
]