from rest_framework import serializers
from django.utils import timezone as django_timezone
from datetime import datetime, timedelta
import pytz
from .models import Event, Enrollment
from apps.activities.models import Activity


class EventSerializer(serializers.ModelSerializer):
    """Serializer for Event model - read operations."""

    activity_code = serializers.CharField(source='activity.code', read_only=True)
    activity_title = serializers.CharField(source='activity.title', read_only=True)
    enrolled_count = serializers.IntegerField(read_only=True)
    attended_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Event
        fields = [
            'id',
            'activity',
            'activity_code',
            'activity_title',
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
            'attended_count'
        ]
        read_only_fields = [
            'id',
            'first_reminder_sent',
            'second_reminder_sent',
            'waiting_email_sent',
            'status',
            'created_at',
            'updated_at'
        ]


class EventCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a single event."""

    activity_code = serializers.CharField(write_only=True)

    class Meta:
        model = Event
        fields = [
            'activity_code',
            'start_datetime',
            'end_datetime',
            'waiting_time_minutes',
            'first_reminder_minutes',
            'second_reminder_minutes'
        ]

    def validate_activity_code(self, value):
        """Validate that activity exists."""
        try:
            activity = Activity.objects.get(code=value)
            return activity
        except Activity.DoesNotExist:
            raise serializers.ValidationError(f"Activity with code '{value}' does not exist.")

    def validate(self, attrs):
        """Validate event dates and times."""
        start = attrs.get('start_datetime')
        end = attrs.get('end_datetime')

        # Validate end is after start
        if end <= start:
            raise serializers.ValidationError({
                'end_datetime': 'End datetime must be after start datetime.'
            })

        # Validate event is in the future
        if start <= django_timezone.now():
            raise serializers.ValidationError({
                'start_datetime': 'Event start datetime must be in the future.'
            })

        # Validate reminders
        first_reminder = attrs.get('first_reminder_minutes')
        second_reminder = attrs.get('second_reminder_minutes')

        if first_reminder and first_reminder < 0:
            raise serializers.ValidationError({
                'first_reminder_minutes': 'First reminder must be positive.'
            })

        if second_reminder and second_reminder < 0:
            raise serializers.ValidationError({
                'second_reminder_minutes': 'Second reminder must be positive.'
            })

        if first_reminder and second_reminder and first_reminder <= second_reminder:
            raise serializers.ValidationError({
                'first_reminder_minutes': 'First reminder must be sent before second reminder.'
            })

        return attrs

    def create(self, validated_data):
        """Create event with activity from validated code."""
        activity = validated_data.pop('activity_code')
        validated_data['activity'] = activity
        return super().create(validated_data)


class EventBulkCreateSerializer(serializers.Serializer):
    """Serializer for bulk creating multiple events."""

    activity_code = serializers.CharField()
    start_date = serializers.DateField(help_text="First day to create events (YYYY-MM-DD)")
    end_date = serializers.DateField(help_text="Last day to create events (YYYY-MM-DD)")
    hours_utc = serializers.ListField(
        child=serializers.CharField(),
        help_text="List of times in UTC (HH:MM format), e.g., ['09:00', '14:00', '18:00']"
    )
    duration_minutes = serializers.IntegerField(default=60, help_text="Duration of each event in minutes")
    waiting_time_minutes = serializers.IntegerField(default=10)
    first_reminder_minutes = serializers.IntegerField(required=False, allow_null=True)
    second_reminder_minutes = serializers.IntegerField(required=False, allow_null=True)

    def validate_activity_code(self, value):
        """Validate that activity exists."""
        try:
            return Activity.objects.get(code=value)
        except Activity.DoesNotExist:
            raise serializers.ValidationError(f"Activity with code '{value}' does not exist.")

    def validate(self, attrs):
        """Validate bulk creation parameters."""
        start_date = attrs['start_date']
        end_date = attrs['end_date']

        # Validate date range
        if end_date < start_date:
            raise serializers.ValidationError({
                'end_date': 'End date must be after or equal to start date.'
            })

        # Validate hours format
        hours = attrs['hours_utc']
        for hour_str in hours:
            try:
                datetime.strptime(hour_str, '%H:%M')
            except ValueError:
                raise serializers.ValidationError({
                    'hours_utc': f"Invalid time format '{hour_str}'. Use HH:MM (e.g., '09:00')."
                })

        # Validate duration
        if attrs['duration_minutes'] <= 0:
            raise serializers.ValidationError({
                'duration_minutes': 'Duration must be positive.'
            })

        return attrs


class EventUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating an event."""

    class Meta:
        model = Event
        fields = [
            'start_datetime',
            'end_datetime',
            'waiting_time_minutes',
            'first_reminder_minutes',
            'second_reminder_minutes'
        ]

    def validate(self, attrs):
        """Validate event updates."""
        instance = self.instance
        start = attrs.get('start_datetime', instance.start_datetime)
        end = attrs.get('end_datetime', instance.end_datetime)

        # Cannot update events that already started
        if instance.start_datetime <= django_timezone.now():
            raise serializers.ValidationError(
                'Cannot update events that have already started or passed.'
            )

        # Validate end is after start
        if end <= start:
            raise serializers.ValidationError({
                'end_datetime': 'End datetime must be after start datetime.'
            })

        return attrs


class EnrollmentSerializer(serializers.ModelSerializer):
    """Serializer for Enrollment model."""

    event_id = serializers.UUIDField(source='event.id', read_only=True)
    event_start = serializers.DateTimeField(source='event.start_datetime', read_only=True)
    event_end = serializers.DateTimeField(source='event.end_datetime', read_only=True)
    activity_code = serializers.CharField(source='event.activity.code', read_only=True)
    activity_title = serializers.CharField(source='event.activity.title', read_only=True)
    user_code = serializers.CharField(source='user.user_code', read_only=True)

    class Meta:
        model = Enrollment
        fields = [
            'id',
            'user',
            'user_code',
            'event',
            'event_id',
            'event_start',
            'event_end',
            'activity_code',
            'activity_title',
            'enrolled_at',
            'status',
            'updated_at'
        ]
        read_only_fields = ['id', 'enrolled_at', 'status', 'updated_at']


class EnrollmentCreateSerializer(serializers.Serializer):
    """Serializer for enrolling in an event."""

    event_id = serializers.UUIDField()

    def validate_event_id(self, value):
        """Validate that event exists and is available."""
        try:
            event = Event.objects.get(id=value)
        except Event.DoesNotExist:
            raise serializers.ValidationError("Event does not exist.")

        # Check if event hasn't started yet
        if event.start_datetime <= django_timezone.now():
            raise serializers.ValidationError("Cannot enroll in events that have already started.")

        # Check if event is active
        if event.activity.is_active is False:
            raise serializers.ValidationError("Cannot enroll in inactive activity.")

        return event

    def create(self, validated_data):
        """Create enrollment."""
        event = validated_data['event_id']
        user = self.context['request'].user

        # Check if already enrolled
        enrollment, created = Enrollment.objects.get_or_create(
            user=user,
            event=event,
            defaults={'status': Enrollment.Status.ENROLLED}
        )

        if not created:
            # If cancelled before, re-enroll
            if enrollment.status == Enrollment.Status.CANCELLED:
                enrollment.status = Enrollment.Status.ENROLLED
                enrollment.save()
            else:
                raise serializers.ValidationError("Already enrolled in this event.")

        return enrollment


class TimezoneConversionSerializer(serializers.Serializer):
    """Serializer for converting times between timezones."""

    datetime_utc = serializers.DateTimeField(help_text="Datetime in UTC")
    target_timezone = serializers.CharField(help_text="Target timezone (e.g., 'America/Mexico_City')")

    def validate_target_timezone(self, value):
        """Validate that timezone is valid."""
        try:
            pytz.timezone(value)
            return value
        except pytz.UnknownTimeZoneError:
            raise serializers.ValidationError(f"Unknown timezone: {value}")

    def to_representation(self, instance):
        """Convert UTC datetime to target timezone."""
        datetime_utc = instance['datetime_utc']
        target_tz = pytz.timezone(instance['target_timezone'])

        # Convert to target timezone
        datetime_local = datetime_utc.astimezone(target_tz)

        return {
            'datetime_utc': datetime_utc.isoformat(),
            'datetime_local': datetime_local.isoformat(),
            'timezone': str(target_tz),
            'offset': datetime_local.strftime('%z')
        }
