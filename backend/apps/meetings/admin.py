from django.contrib import admin
from .models import Meeting, MeetingParticipant


class MeetingParticipantInline(admin.TabularInline):
    """Inline admin for meeting participants."""
    model = MeetingParticipant
    extra = 0
    readonly_fields = ('joined_at', 'updated_at')
    can_delete = False


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    """Admin configuration for Meeting model."""

    list_display = (
        'meeting_id',
        'event',
        'meeting_provider',
        'start_time',
        'end_time',
        'participant_count',
        'created_at'
    )
    list_filter = ('meeting_provider', 'start_time', 'event__activity')
    search_fields = ('meeting_id', 'meeting_url', 'event__activity__code')
    readonly_fields = ('created_at', 'participant_count')
    inlines = [MeetingParticipantInline]

    fieldsets = (
        ('Event', {
            'fields': ('event',)
        }),
        ('Meeting Details', {
            'fields': ('meeting_provider', 'meeting_id', 'meeting_url')
        }),
        ('Time', {
            'fields': ('start_time', 'end_time')
        }),
        ('Statistics', {
            'fields': ('participant_count',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(MeetingParticipant)
class MeetingParticipantAdmin(admin.ModelAdmin):
    """Admin configuration for MeetingParticipant model."""

    list_display = ('user', 'meeting', 'status', 'joined_at', 'updated_at')
    list_filter = ('status', 'joined_at', 'meeting__meeting_provider')
    search_fields = ('user__user_code', 'user__email', 'meeting__meeting_id')
    readonly_fields = ('joined_at', 'updated_at')

    fieldsets = (
        (None, {
            'fields': ('meeting', 'user', 'status')
        }),
        ('Timestamps', {
            'fields': ('joined_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
