from django.urls import path
from . import views

app_name = 'company'  # <- Muy importante

urlpatterns = [
    path('create-job/', views.create_job_view, name='create_job'),
    path('edit-job/<int:job_id>/', views.edit_job_view, name='edit_job'),
    path('toggle-job/<int:job_id>/', views.toggle_job_status, name='toggle_job'),

    path('validate-language/', views.validate_language_ajax, name='validate_language'),

    # Gestión de informes de contratación (Ley 2466/2025)
    path('hiring-reports/', views.hiring_reports_list_view, name='hiring_reports'),
    path('hiring-reports/create/', views.create_hiring_report_view, name='create_hiring_report'),
    path('hiring-reports/<int:report_id>/', views.hiring_report_detail_view, name='hiring_report_detail'),
    path('hiring-reports/<int:report_id>/edit/', views.edit_hiring_report_view, name='edit_hiring_report'),
    path('hiring-reports/<int:report_id>/delete/', views.delete_hiring_report_view, name='delete_hiring_report'),
    path('hiring-reports/<int:report_id>/send/', views.send_hiring_report_view, name='send_hiring_report'),
    
    # ESTAS SON LAS QUE FALTABAN - DESCARGAS EN TIEMPO REAL
    path('hiring-reports/<int:report_id>/download-pdf/', views.download_my_report_pdf, name='download_report_pdf'),
    path('hiring-reports/<int:report_id>/download-xml/', views.download_my_report_xml, name='download_report_xml'),

    path('quota-compliance/', views.quota_compliance_dashboard, name='quota_compliance'),
    path('quota-compliance/update-employees/', views.update_employee_count, name='update_employees'),
    path('quota-compliance/export-pdf/', views.export_quota_report_pdf, name='export_quota_pdf'),
    path('quota-compliance/export-excel/', views.export_quota_report_excel, name='export_quota_excel'),
]