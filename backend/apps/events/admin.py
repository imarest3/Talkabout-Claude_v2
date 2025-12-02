from django.contrib import admin
from .models import Event, Enrollment


class EnrollmentInline(admin.TabularInline):
    """Inline admin for enrollments."""
    model = Enrollment
    extra = 0
    readonly_fields = ('enrolled_at', 'unsubscribe_token', 'updated_at')
    can_delete = False


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    """Admin configuration for Event model."""

    list_display = (
        'activity',
        'start_datetime',
        'end_datetime',
        'status',
        'get_enrolled_count',
        'get_attended_count',
        'created_at'
    )
    list_filter = ('status', 'start_datetime', 'activity')
    search_fields = ('activity__code', 'activity__title')
    readonly_fields = (
        'created_at',
        'updated_at',
        'first_reminder_sent',
        'second_reminder_sent',
        'waiting_email_sent',
        'get_enrolled_count',
        'get_attended_count'
    )
    inlines = [EnrollmentInline]

    fieldsets = (
        ('Activity', {
            'fields': ('activity', 'status')
        }),
        ('Date & Time', {
            'fields': ('start_datetime', 'end_datetime', 'waiting_time_minutes')
        }),
        ('Reminders', {
            'fields': (
                'first_reminder_minutes',
                'first_reminder_sent',
                'second_reminder_minutes',
                'second_reminder_sent',
                'waiting_email_sent'
            )
        }),
        ('Statistics', {
            'fields': ('get_enrolled_count', 'get_attended_count'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    @admin.display(description='Enrolled')
    def get_enrolled_count(self, obj):
        """Get count of enrolled users."""
        return obj.enrollments.filter(status=Enrollment.Status.ENROLLED).count()

    @admin.display(description='Attended')
    def get_attended_count(self, obj):
        """Get count of attended users."""
        return obj.enrollments.filter(status=Enrollment.Status.ATTENDED).count()


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    """Admin configuration for Enrollment model."""

    list_display = ('user', 'event', 'status', 'enrolled_at')
    list_filter = ('status', 'enrolled_at', 'event__activity')
    search_fields = ('user__user_code', 'user__email', 'event__activity__code')
    readonly_fields = ('enrolled_at', 'unsubscribe_token', 'updated_at')

    fieldsets = (
        (None, {
            'fields': ('user', 'event', 'status')
        }),
        ('Tokens', {
            'fields': ('unsubscribe_token',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('enrolled_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
