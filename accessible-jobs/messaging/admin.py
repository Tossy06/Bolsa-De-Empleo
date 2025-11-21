# messaging/admin.py
from django.contrib import admin
from .models import Conversation, Message, MessageNotification


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['subject', 'candidate', 'company', 'created_at', 'updated_at']
    list_filter = ['created_at', 'is_archived_by_candidate', 'is_archived_by_company']
    search_fields = ['subject', 'job_title', 'candidate__email', 'company__email']
    readonly_fields = ['created_at', 'updated_at', 'candidate_last_read', 'company_last_read']
    ordering = ['-updated_at']
    
    fieldsets = (
        ('Participantes', {
            'fields': ('candidate', 'company')
        }),
        ('Detalles', {
            'fields': ('subject', 'job_title')
        }),
        ('Estado', {
            'fields': ('is_archived_by_candidate', 'is_archived_by_company', 
                      'candidate_last_read', 'company_last_read')
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['conversation', 'sender', 'created_at', 'is_read']
    list_filter = ['is_read', 'created_at']
    search_fields = ['conversation__subject', 'sender__email', 'content']
    readonly_fields = ['created_at', 'read_at', 'attachment_size']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Conversación', {
            'fields': ('conversation', 'sender')
        }),
        ('Contenido', {
            'fields': ('content', 'attachment', 'attachment_alt_text', 'attachment_size')
        }),
        ('Estado', {
            'fields': ('is_read', 'read_at')
        }),
        ('Fecha', {
            'fields': ('created_at',)
        }),
    )


@admin.register(MessageNotification)
class MessageNotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'message', 'is_read', 'is_email_sent', 'created_at']
    list_filter = ['is_read', 'is_email_sent', 'created_at']
    search_fields = ['user__email', 'message__content']
    readonly_fields = ['created_at']
    ordering = ['-created_at']