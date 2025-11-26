from rest_framework import serializers

from .models import Event


class EventSerializer(serializers.ModelSerializer):
    """Serializer for Event model."""

    enrolled_count = serializers.IntegerField(read_only=True)
    attended_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Event
        fields = [
            'id',
            'activity',
            'start_datetime',
            'end_datetime',
            'waiting_time_minutes',
            'first_reminder_minutes',
            'second_reminder_minutes',
            'first_reminder_sent',
            'second_reminder_sent',
            'waiting_email_sent',
            'status',
            'created_at',
            'updated_at',
            'enrolled_count',
            'attended_count',
        ]
        read_only_fields = [
            'id',
            'created_at',
            'updated_at',
            'first_reminder_sent',
            'second_reminder_sent',
            'waiting_email_sent',
            'enrolled_count',
            'attended_count',
        ]
