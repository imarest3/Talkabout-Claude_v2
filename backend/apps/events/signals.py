"""
Django signals for automatic email notifications.
"""
import logging
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Enrollment
from .emails import send_enrollment_confirmation, send_cancellation_confirmation

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Enrollment)
def send_enrollment_emails(sender, instance, created, **kwargs):
    """
    Send appropriate emails when enrollment is created or updated.

    Args:
        sender: The model class (Enrollment)
        instance: The actual instance being saved
        created: Boolean indicating if this is a new instance
        **kwargs: Additional keyword arguments
    """
    # Only send emails if user has an email address
    if not instance.user.email:
        logger.warning(f'User {instance.user.user_code} has no email address')
        return

    if created:
        # New enrollment - send confirmation
        logger.info(f'New enrollment created for user {instance.user.user_code} in event {instance.event.id}')
        send_enrollment_confirmation(instance)

    else:
        # Existing enrollment updated - check if status changed to cancelled
        if instance.status == Enrollment.Status.CANCELLED:
            logger.info(f'Enrollment cancelled for user {instance.user.user_code} in event {instance.event.id}')
            send_cancellation_confirmation(instance)


@receiver(pre_save, sender=Enrollment)
def track_status_change(sender, instance, **kwargs):
    """
    Track status changes to determine if cancellation email should be sent.

    This runs before save to capture the old state.
    """
    if instance.pk:  # Only for existing enrollments
        try:
            old_instance = Enrollment.objects.get(pk=instance.pk)
            instance._old_status = old_instance.status
        except Enrollment.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None
