from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Administración personalizada de usuarios
    """
    list_display = [
        'username',
        'email',
        'full_name',
        'user_type_badge',
        'disability_badge',
        'is_active_icon',
        'email_verified_icon',
        'is_staff',
        'created_at',
    ]
    
    list_filter = [
        'user_type',
        'is_active',
        'is_staff',
        'is_superuser',
        'email_verified',
        'disability_type',
        'requires_screen_reader',
        'high_contrast_mode',
        'large_text_mode',
        'created_at',
    ]
    
    search_fields = [
        'username',
        'email',
        'first_name',
        'last_name',
        'phone',
    ]
    
    ordering = ['-created_at']
    
    fieldsets = (
        ('Información de Autenticación', {
            'fields': ('username', 'password')
        }),
        ('Información Personal', {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'profile_picture')
        }),
        ('Tipo de Usuario', {
            'fields': ('user_type',)
        }),
        ('Configuración de Accesibilidad', {
            'fields': (
                'disability_type',
                'requires_screen_reader',
                'high_contrast_mode',
                'large_text_mode',
            ),
            'classes': ('collapse',),
        }),
        ('Verificación y Estado', {
            'fields': (
                'email_verified',
                'is_active',
            ),
        }),
        ('Permisos', {
            'fields': (
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions',
            ),
            'classes': ('collapse',),
        }),
        ('Fechas Importantes', {
            'fields': ('last_login', 'date_joined', 'created_at', 'updated_at'),
        }),
    )
    
    add_fieldsets = (
        ('Información de Autenticación', {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
        ('Tipo de Usuario', {
            'fields': ('user_type',),
        }),
        ('Información Personal', {
            'classes': ('collapse',),
            'fields': ('first_name', 'last_name', 'phone'),
        }),
    )
    
    readonly_fields = ['date_joined', 'last_login', 'created_at', 'updated_at']
    
    actions = ['verify_emails', 'activate_users', 'deactivate_users']
    
    def full_name(self, obj):
        """Muestra el nombre completo del usuario"""
        full = obj.get_full_name()
        return full if full != obj.username else f"{obj.username} (sin nombre)"
    full_name.short_description = 'Nombre Completo'
    full_name.admin_order_field = 'first_name'
    
    def user_type_badge(self, obj):
        """Muestra un badge con el tipo de usuario"""
        colors = {
            'candidate': '#007bff',
            'company': '#28a745',
            'admin': '#dc3545',
        }
        icons = {
            'candidate': '👤',
            'company': '🏢',
            'admin': '⚙️',
        }
        color = colors.get(obj.user_type, '#6c757d')
        icon = icons.get(obj.user_type, '❓')
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-size: 11px; font-weight: bold;">{} {}</span>',
            color,
            icon,
            obj.get_user_type_display()
        )
    user_type_badge.short_description = 'Tipo de Usuario'
    user_type_badge.admin_order_field = 'user_type'
    
    def disability_badge(self, obj):
        """Muestra badge de tipo de discapacidad"""
        if obj.disability_type in ['none', 'prefer_not_say']:
            return '—'
        
        icons = {
            'visual': '👁️',
            'auditive': '👂',
            'motor': '♿',
            'cognitive': '🧠',
            'multiple': '🔄',
            'other': '❓',
        }
        colors = {
            'visual': '#17a2b8',
            'auditive': '#ffc107',
            'motor': '#28a745',
            'cognitive': '#6f42c1',
            'multiple': '#fd7e14',
            'other': '#6c757d',
        }
        
        icon = icons.get(obj.disability_type, '❓')
        color = colors.get(obj.disability_type, '#6c757d')
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px;" title="{}">{} {}</span>',
            color,
            obj.get_disability_type_display(),
            icon,
            obj.get_disability_type_display()
        )
    disability_badge.short_description = 'Discapacidad'
    disability_badge.admin_order_field = 'disability_type'
    
    def is_active_icon(self, obj):
        """Muestra un ícono de estado activo/inactivo"""
        if obj.is_active:
            return format_html(
                '<span style="color: green; font-size: 18px;" title="Activo">✓</span>'
            )
        return format_html(
            '<span style="color: red; font-size: 18px;" title="Inactivo">✗</span>'
        )
    is_active_icon.short_description = 'Activo'
    is_active_icon.admin_order_field = 'is_active'
    
    def email_verified_icon(self, obj):
        """Muestra un ícono de email verificado/no verificado"""
        if obj.email_verified:
            return format_html(
                '<span style="color: green; font-size: 16px;" title="Email verificado">✓</span>'
            )
        return format_html(
            '<span style="color: orange; font-size: 16px;" title="Email no verificado">⏳</span>'
        )
    email_verified_icon.short_description = 'Email'
    email_verified_icon.admin_order_field = 'email_verified'
    
    # Acciones personalizadas
    def verify_emails(self, request, queryset):
        """Marcar emails como verificados"""
        count = queryset.filter(email_verified=False).update(email_verified=True)
        self.message_user(
            request,
            f'{count} usuario(s) marcado(s) con email verificado.'
        )
    verify_emails.short_description = 'Verificar emails seleccionados'
    
    def activate_users(self, request, queryset):
        """Activar usuarios"""
        count = queryset.filter(is_active=False).update(is_active=True)
        self.message_user(
            request,
            f'{count} usuario(s) activado(s).'
        )
    activate_users.short_description = 'Activar usuarios seleccionados'
    
    def deactivate_users(self, request, queryset):
        """Desactivar usuarios"""
        count = queryset.filter(is_active=True).update(is_active=False)
        self.message_user(
            request,
            f'{count} usuario(s) desactivado(s).'
        )
    deactivate_users.short_description = 'Desactivar usuarios seleccionados'
    
    def get_queryset(self, request):
        """Optimiza las consultas"""
        qs = super().get_queryset(request)
        return qs