from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Task, AuditLog

class CustomUserAdmin(UserAdmin):
    """Custom admin interface for User model"""
    list_display = ('username', 'email', 'role', 'is_staff', 'is_superuser', 'date_joined')
    list_filter = ('role', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email')
    
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('role', 'two_factor_enabled', 'two_factor_code', 'two_factor_code_created')}),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Fields', {'fields': ('role',)}),
    )

class TaskAdmin(admin.ModelAdmin):
    """Admin interface for Task model"""
    list_display = ('title', 'created_by', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at')
    search_fields = ('title', 'description', 'created_by__username')
    readonly_fields = ('created_at', 'updated_at')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('created_by')

class AuditLogAdmin(admin.ModelAdmin):
    """Admin interface for AuditLog model"""
    list_display = ('timestamp', 'user', 'action', 'details', 'ip_address')
    list_filter = ('action', 'timestamp')
    search_fields = ('user__username', 'action', 'details', 'ip_address')
    readonly_fields = ('timestamp', 'user', 'action', 'details', 'ip_address')
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False

# Register models with admin site
admin.site.register(User, CustomUserAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(AuditLog, AuditLogAdmin)