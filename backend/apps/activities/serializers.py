from rest_framework import serializers
from .models import Activity, ActivityFile
from apps.users.models import User


class ActivityFileSerializer(serializers.ModelSerializer):
    """Serializer for ActivityFile model."""

    file_url = serializers.SerializerMethodField()

    class Meta:
        model = ActivityFile
        fields = ['id', 'filename', 'file', 'file_url', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']

    def get_file_url(self, obj):
        """Get full URL for the file."""
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return None


class ActivitySerializer(serializers.ModelSerializer):
    """Serializer for Activity model - read operations."""

    files = ActivityFileSerializer(many=True, read_only=True)
    created_by_name = serializers.SerializerMethodField()
    event_count = serializers.SerializerMethodField()

    class Meta:
        model = Activity
        fields = [
            'id',
            'code',
            'title',
            'description',
            'max_participants_per_meeting',
            'created_by',
            'created_by_name',
            'is_active',
            'created_at',
            'updated_at',
            'files',
            'event_count'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']

    def get_created_by_name(self, obj):
        """Get creator's user_code."""
        return obj.created_by.user_code if obj.created_by else None

    def get_event_count(self, obj):
        """Get count of events for this activity."""
        return obj.events.count()


class ActivityCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating activities."""

    class Meta:
        model = Activity
        fields = [
            'code',
            'title',
            'description',
            'max_participants_per_meeting',
            'is_active'
        ]

    def validate_code(self, value):
        """Validate that activity code is unique."""
        # For update operations, exclude current instance
        instance = self.instance
        qs = Activity.objects.filter(code=value)

        if instance:
            qs = qs.exclude(pk=instance.pk)

        if qs.exists():
            raise serializers.ValidationError("Activity with this code already exists.")

        return value

    def validate_max_participants_per_meeting(self, value):
        """Validate max participants is at least 2."""
        if value < 2:
            raise serializers.ValidationError(
                "Maximum participants per meeting must be at least 2."
            )
        return value

    def create(self, validated_data):
        """Create activity with current user as creator."""
        request = self.context.get('request')
        validated_data['created_by'] = request.user
        return super().create(validated_data)


class ActivityFileUploadSerializer(serializers.ModelSerializer):
    """Serializer for uploading files to an activity."""

    class Meta:
        model = ActivityFile
        fields = ['file', 'filename']

    def validate_file(self, value):
        """Validate file size and type."""
        # Limit file size to 10MB
        max_size = 10 * 1024 * 1024  # 10MB in bytes

        if value.size > max_size:
            raise serializers.ValidationError(
                f"File size cannot exceed 10MB. Current size: {value.size / (1024*1024):.2f}MB"
            )

        return value

    def create(self, validated_data):
        """Create file with activity from context."""
        activity = self.context.get('activity')
        validated_data['activity'] = activity

        # Auto-set filename if not provided
        if not validated_data.get('filename') and validated_data.get('file'):
            validated_data['filename'] = validated_data['file'].name

        return super().create(validated_data)
