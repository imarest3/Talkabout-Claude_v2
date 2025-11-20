import uuid
from django.db import models
from django.utils.timezone import now as timezone_now
from apps.events.models import Event
from apps.users.models import User


class Meeting(models.Model):
    """Meeting model representing a video conference session."""

    class Provider(models.TextChoices):
        GOOGLE_MEET = 'google_meet', 'Google Meet'
        JITSI = 'jitsi', 'Jitsi'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='meetings'
    )
    meeting_url = models.URLField(max_length=500)
    meeting_provider = models.CharField(
        max_length=20,
        choices=Provider.choices,
        default=Provider.JITSI
    )
    meeting_id = models.CharField(
        max_length=255,
        db_index=True,
        help_text="Meeting ID from the provider"
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone_now)

    class Meta:
        db_table = 'meetings'
        verbose_name = 'Meeting'
        verbose_name_plural = 'Meetings'
        ordering = ['start_time']
        indexes = [
            models.Index(fields=['event', 'start_time']),
            models.Index(fields=['meeting_id']),
        ]

    def __str__(self):
        return f"Meeting {self.meeting_id} - {self.event}"

    @property
    def participant_count(self):
        """Get count of participants who joined."""
        return self.participants.filter(status=MeetingParticipant.Status.JOINED).count()


class MeetingParticipant(models.Model):
    """MeetingParticipant model tracking user participation in meetings."""

    class Status(models.TextChoices):
        WAITING = 'waiting', 'Waiting'
        JOINED = 'joined', 'Joined'
        LEFT = 'left', 'Left'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    meeting = models.ForeignKey(
        Meeting,
        on_delete=models.CASCADE,
        related_name='participants'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='meeting_participations'
    )
    joined_at = models.DateTimeField(default=timezone_now)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.WAITING,
        db_index=True
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'meeting_participants'
        verbose_name = 'Meeting Participant'
        verbose_name_plural = 'Meeting Participants'
        ordering = ['joined_at']
        unique_together = [['meeting', 'user']]
        indexes = [
            models.Index(fields=['meeting', 'status']),
            models.Index(fields=['user', 'status']),
        ]

    def __str__(self):
        return f"{self.user.user_code} in {self.meeting.meeting_id}"

    def mark_joined(self):
        """Mark participant as joined."""
        self.status = self.Status.JOINED
        self.save()

    def mark_left(self):
        """Mark participant as left."""
        self.status = self.Status.LEFT
        self.save()
