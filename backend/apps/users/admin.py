from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin configuration for User model."""

    list_display = ('user_code', 'email', 'role', 'is_active', 'is_anonymized', 'created_at')
    list_filter = ('role', 'is_active', 'is_anonymized', 'created_at')
    search_fields = ('user_code', 'email')
    ordering = ('-created_at',)

    fieldsets = (
        (None, {'fields': ('user_code', 'password')}),
        ('Personal info', {'fields': ('email', 'timezone')}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'is_anonymized')}),
        ('Important dates', {'fields': ('last_login', 'created_at', 'updated_at')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('user_code', 'email', 'password1', 'password2', 'role', 'timezone'),
        }),
    )

    readonly_fields = ('created_at', 'updated_at', 'last_login')
