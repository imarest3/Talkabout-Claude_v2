from rest_framework import serializers
from .models import Meeting, MeetingParticipant


class MeetingParticipantSerializer(serializers.ModelSerializer):
    """Serializer for meeting participants (privacy-focused)."""
    user_code = serializers.CharField(source='user.user_code', read_only=True)

    class Meta:
        model = MeetingParticipant
        fields = ['id', 'user_code', 'status', 'joined_at']
        read_only_fields = ['id', 'joined_at']


class MeetingSerializer(serializers.ModelSerializer):
    """Serializer for returning meeting details to the assigned user."""
    participants = MeetingParticipantSerializer(many=True, read_only=True)
    participant_count = serializers.SerializerMethodField()

    def get_participant_count(self, obj):
        return obj.participants.count()

    class Meta:
        model = Meeting
        fields = [
            'id', 
            'event', 
            'meeting_url', 
            'meeting_provider', 
            'meeting_id', 
            'start_time', 
            'end_time', 
            'participants',
            'participant_count'
        ]
        read_only_fields = [
            'id', 
            'event', 
            'meeting_url', 
            'meeting_provider', 
            'meeting_id', 
            'start_time', 
            'end_time',
            'participant_count'
        ]
