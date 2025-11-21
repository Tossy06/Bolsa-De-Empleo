# complaints/admin.py
from django.contrib import admin
from .models import Complaint, ComplaintComment, ComplaintStatusHistory


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ['tracking_code', 'complaint_type', 'subject', 'status', 'priority', 'created_at']
    list_filter = ['status', 'complaint_type', 'priority', 'is_anonymous', 'created_at']
    search_fields = ['tracking_code', 'subject', 'company_name', 'complainant_email']
    readonly_fields = ['tracking_code', 'created_at', 'updated_at', 'resolved_at', 'ip_address', 'user_agent']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('tracking_code', 'complaint_type', 'subject', 'description')
        }),
        ('Denunciado', {
            'fields': ('company_name', 'job_posting_url')
        }),
        ('Denunciante', {
            'fields': ('is_anonymous', 'complainant_user', 'complainant_name', 'complainant_email', 'complainant_phone')
        }),
        ('Evidencias', {
            'fields': ('evidence_file1', 'evidence_file2', 'evidence_file3')
        }),
        ('Gestión', {
            'fields': ('status', 'priority', 'assigned_to', 'admin_response')
        }),
        ('Auditoría', {
            'fields': ('ip_address', 'user_agent', 'created_at', 'updated_at', 'resolved_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ComplaintComment)
class ComplaintCommentAdmin(admin.ModelAdmin):
    list_display = ['complaint', 'author', 'is_internal', 'created_at']
    list_filter = ['is_internal', 'created_at']
    search_fields = ['complaint__tracking_code', 'comment', 'author__email']
    readonly_fields = ['created_at']


@admin.register(ComplaintStatusHistory)
class ComplaintStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ['complaint', 'previous_status', 'new_status', 'changed_by', 'created_at']
    list_filter = ['previous_status', 'new_status', 'created_at']
    search_fields = ['complaint__tracking_code', 'reason']
    readonly_fields = ['created_at']