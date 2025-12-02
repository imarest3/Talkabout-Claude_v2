import uuid
import secrets
from django.db import models
from django.utils.timezone import now as timezone_now
from apps.activities.models import Activity
from apps.users.models import User


class Event(models.Model):
    """Event model representing a specific time slot for an activity."""

    class Status(models.TextChoices):
        SCHEDULED = 'scheduled', 'Scheduled'
        IN_WAITING = 'in_waiting', 'In Waiting Room'
        IN_PROGRESS = 'in_progress', 'In Progress'
        COMPLETED = 'completed', 'Completed'
        CANCELLED = 'cancelled', 'Cancelled'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    activity = models.ForeignKey(
        Activity,
        on_delete=models.CASCADE,
        related_name='events'
    )
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    waiting_time_minutes = models.PositiveIntegerField(
        default=10,
        help_text="Minutes before start to open waiting room"
    )
    first_reminder_minutes = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Minutes before start to send first reminder"
    )
    second_reminder_minutes = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Minutes before start to send second reminder"
    )
    first_reminder_sent = models.BooleanField(default=False)
    second_reminder_sent = models.BooleanField(default=False)
    waiting_email_sent = models.BooleanField(default=False)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.SCHEDULED,
        db_index=True
    )
    created_at = models.DateTimeField(default=timezone_now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'events'
        verbose_name = 'Event'
        verbose_name_plural = 'Events'
        ordering = ['start_datetime']
        indexes = [
            models.Index(fields=['activity', 'start_datetime']),
            models.Index(fields=['status', 'start_datetime']),
        ]

    def __str__(self):
        return f"{self.activity.code} - {self.start_datetime}"


class Enrollment(models.Model):
    """Enrollment model linking users to events."""

    class Status(models.TextChoices):
        ENROLLED = 'enrolled', 'Enrolled'
        CANCELLED = 'cancelled', 'Cancelled'
        ATTENDED = 'attended', 'Attended'
        NO_SHOW = 'no_show', 'No Show'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    enrolled_at = models.DateTimeField(default=timezone_now)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ENROLLED,
        db_index=True
    )
    unsubscribe_token = models.CharField(
        max_length=64,
        unique=True,
        db_index=True,
        editable=False
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'enrollments'
        verbose_name = 'Enrollment'
        verbose_name_plural = 'Enrollments'
        ordering = ['-enrolled_at']
        unique_together = [['user', 'event']]
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['event', 'status']),
        ]

    def __str__(self):
        return f"{self.user.user_code} -> {self.event}"

    def save(self, *args, **kwargs):
        """Generate unsubscribe token on creation."""
        if not self.unsubscribe_token:
            self.unsubscribe_token = secrets.token_urlsafe(32)
        super().save(*args, **kwargs)

    def cancel(self):
        """Cancel this enrollment."""
        self.status = self.Status.CANCELLED
        self.save()

    def mark_attended(self):
        """Mark user as attended."""
        self.status = self.Status.ATTENDED
        self.save()

    def mark_no_show(self):
        """Mark user as no-show."""
        self.status = self.Status.NO_SHOW
        self.save()
