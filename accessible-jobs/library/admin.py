# library/admin.py
from django.contrib import admin
from .models import ResourceCategory, BestPracticeResource, ResourceBookmark


@admin.register(ResourceCategory)
class ResourceCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'order', 'is_active', 'get_resources_count']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}  # ✅ CORREGIDO: 'name' en lugar de 'title'
    ordering = ['order', 'name']


@admin.register(BestPracticeResource)
class BestPracticeResourceAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'resource_type', 'is_published', 'is_featured', 'view_count', 'download_count', 'created_at']
    list_filter = ['category', 'resource_type', 'is_published', 'is_featured', 'is_accessible']
    search_fields = ['title', 'description', 'tags', 'author']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['view_count', 'download_count', 'created_at', 'updated_at', 'file_size']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('title', 'slug', 'category', 'resource_type', 'description')
        }),
        ('Contenido', {
            'fields': ('content', 'file', 'file_size', 'external_url')
        }),
        ('Metadatos', {
            'fields': ('author', 'publication_date', 'tags')
        }),
        ('Accesibilidad', {
            'fields': ('is_accessible', 'accessibility_notes')
        }),
        ('Publicación', {
            'fields': ('is_published', 'is_featured')
        }),
        ('Estadísticas', {
            'fields': ('view_count', 'download_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ResourceBookmark)
class ResourceBookmarkAdmin(admin.ModelAdmin):
    list_display = ['user', 'resource', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__first_name', 'user__last_name', 'resource__title']
    readonly_fields = ['created_at']