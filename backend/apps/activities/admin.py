from django.contrib import admin
from .models import Activity, ActivityFile


class ActivityFileInline(admin.TabularInline):
    """Inline admin for activity files."""
    model = ActivityFile
    extra = 1
    readonly_fields = ('uploaded_at',)


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    """Admin configuration for Activity model."""

    list_display = ('code', 'title', 'created_by', 'max_participants_per_meeting', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at', 'created_by')
    search_fields = ('code', 'title', 'description')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [ActivityFileInline]

    fieldsets = (
        (None, {
            'fields': ('code', 'title', 'description')
        }),
        ('Configuration', {
            'fields': ('max_participants_per_meeting', 'created_by', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ActivityFile)
class ActivityFileAdmin(admin.ModelAdmin):
    """Admin configuration for ActivityFile model."""

    list_display = ('filename', 'activity', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('filename', 'activity__code', 'activity__title')
    readonly_fields = ('uploaded_at',)
