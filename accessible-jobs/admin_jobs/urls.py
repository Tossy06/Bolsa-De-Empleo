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

    # Rutas del "Ministerio" (simulación)
    path('ministry/', views.ministry_dashboard_view, name='ministry_dashboard'),
    path('ministry/reports/', views.ministry_reports_list_view, name='ministry_reports_list'),
    path('ministry/reports/<int:report_id>/', views.ministry_report_detail_view, name='ministry_report_detail'),
    path('ministry/reports/<int:report_id>/download-pdf/', views.download_report_pdf, name='download_report_pdf'),
    path('ministry/reports/<int:report_id>/download-xml/', views.download_report_xml, name='download_report_xml'),

    # Dashboard de KPIs de Inclusión
    path('kpis/', views.inclusion_kpis_dashboard, name='inclusion_kpis'),
    path('kpis/export-pdf/', views.export_kpis_pdf, name='export_kpis_pdf'),
]