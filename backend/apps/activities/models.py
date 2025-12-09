import uuid
import os
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.timezone import now as timezone_now
from apps.users.models import User


def validate_file_extension(value):
    """Validate that uploaded file has an allowed extension."""
    # Allowed extensions (safe file types)
    allowed_extensions = [
        '.pdf', '.doc', '.docx', '.txt', '.rtf',  # Documents
        '.xls', '.xlsx', '.csv',  # Spreadsheets
        '.ppt', '.pptx',  # Presentations
        '.jpg', '.jpeg', '.png', '.gif', '.svg',  # Images
        '.mp3', '.mp4', '.wav', '.avi', '.mov',  # Media
        '.zip', '.rar',  # Archives
    ]

    ext = os.path.splitext(value.name)[1].lower()
    if ext not in allowed_extensions:
        raise ValidationError(
            f'Unsupported file extension: {ext}. '
            f'Allowed extensions: {", ".join(allowed_extensions)}'
        )


def validate_file_size(value):
    """Validate that uploaded file size is within limit (max 50MB)."""
    max_size = 50 * 1024 * 1024  # 50 MB in bytes
    if value.size > max_size:
        raise ValidationError(
            f'File size too large. Maximum allowed size is 50MB. '
            f'Your file is {round(value.size / (1024 * 1024), 2)}MB.'
        )


class Activity(models.Model):
    """Activity model representing a conversation task."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=50, unique=True, db_index=True)
    title = models.CharField(max_length=255)
    description = models.TextField(help_text="HTML description of the activity")
    max_participants_per_meeting = models.PositiveIntegerField(default=6)
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_activities',
        limit_choices_to={'role__in': [User.Role.TEACHER, User.Role.ADMIN]}
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone_now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'activities'
        verbose_name = 'Activity'
        verbose_name_plural = 'Activities'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.code}: {self.title}"


class ActivityFile(models.Model):
    """File attachment for an activity."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    activity = models.ForeignKey(
        Activity,
        on_delete=models.CASCADE,
        related_name='files'
    )
    file = models.FileField(
        upload_to='activity_files/%Y/%m/%d/',
        validators=[validate_file_extension, validate_file_size]
    )
    filename = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(default=timezone_now)

    class Meta:
        db_table = 'activity_files'
        verbose_name = 'Activity File'
        verbose_name_plural = 'Activity Files'
        ordering = ['uploaded_at']

    def __str__(self):
        return f"{self.filename} - {self.activity.code}"

    def save(self, *args, **kwargs):
        """Auto-populate filename from uploaded file if not set."""
        if not self.filename and self.file:
            self.filename = self.file.name
        super().save(*args, **kwargs)
