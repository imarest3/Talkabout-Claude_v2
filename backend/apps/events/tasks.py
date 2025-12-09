"""
Celery tasks for event notifications and reminders.
"""
import logging
from datetime import timedelta
from django.utils import timezone
from celery import shared_task

from .models import Event, Enrollment
from .emails import (
    send_first_reminder,
    send_second_reminder,
    send_waiting_room_notification
)

logger = logging.getLogger(__name__)


@shared_task
def send_first_reminders():
    """
    Celery task to send first reminders for upcoming events.

    This task should be run periodically (e.g., every 5 minutes) to check
    for events that need first reminders.
    """
    now = timezone.now()
    logger.info(f'Running first reminder task at {now}')

    # Find events that need first reminders
    events = Event.objects.filter(
        status=Event.Status.SCHEDULED,
        first_reminder_sent=False,
        first_reminder_minutes__isnull=False
    )

    reminders_sent = 0

    for event in events:
        # Calculate when the reminder should be sent
        reminder_time = event.start_datetime - timedelta(minutes=event.first_reminder_minutes)

        # Send if we've passed the reminder time
        if now >= reminder_time:
            logger.info(f'Sending first reminders for event {event.id}')

            # Get all enrolled users
            enrollments = event.enrollments.filter(status=Enrollment.Status.ENROLLED)

            for enrollment in enrollments:
                if enrollment.user.email:
                    send_first_reminder(enrollment)
                    reminders_sent += 1

            # Mark as sent
            event.first_reminder_sent = True
            event.save()

    logger.info(f'First reminder task completed. Sent {reminders_sent} reminders.')
    return f'Sent {reminders_sent} first reminders'


@shared_task
def send_second_reminders():
    """
    Celery task to send second reminders for upcoming events.

    This task should be run periodically (e.g., every 5 minutes).
    """
    now = timezone.now()
    logger.info(f'Running second reminder task at {now}')

    # Find events that need second reminders
    events = Event.objects.filter(
        status=Event.Status.SCHEDULED,
        second_reminder_sent=False,
        second_reminder_minutes__isnull=False
    )

    reminders_sent = 0

    for event in events:
        # Calculate when the reminder should be sent
        reminder_time = event.start_datetime - timedelta(minutes=event.second_reminder_minutes)

        # Send if we've passed the reminder time
        if now >= reminder_time:
            logger.info(f'Sending second reminders for event {event.id}')

            # Get all enrolled users
            enrollments = event.enrollments.filter(status=Enrollment.Status.ENROLLED)

            for enrollment in enrollments:
                if enrollment.user.email:
                    send_second_reminder(enrollment)
                    reminders_sent += 1

            # Mark as sent
            event.second_reminder_sent = True
            event.save()

    logger.info(f'Second reminder task completed. Sent {reminders_sent} reminders.')
    return f'Sent {reminders_sent} second reminders'


@shared_task
def send_waiting_room_notifications():
    """
    Celery task to send waiting room notifications when the room opens.

    This task should be run periodically (e.g., every minute).
    """
    now = timezone.now()
    logger.info(f'Running waiting room notification task at {now}')

    # Find events where waiting room should open
    events = Event.objects.filter(
        status=Event.Status.SCHEDULED,
        waiting_email_sent=False
    )

    notifications_sent = 0

    for event in events:
        # Calculate when waiting room opens
        waiting_room_time = event.start_datetime - timedelta(minutes=event.waiting_time_minutes)

        # Send if we've reached or passed the waiting room open time
        if now >= waiting_room_time:
            logger.info(f'Sending waiting room notifications for event {event.id}')

            # Get all enrolled users
            enrollments = event.enrollments.filter(status=Enrollment.Status.ENROLLED)

            for enrollment in enrollments:
                if enrollment.user.email:
                    send_waiting_room_notification(enrollment)
                    notifications_sent += 1

            # Mark as sent and update event status
            event.waiting_email_sent = True
            event.status = Event.Status.IN_WAITING
            event.save()

    logger.info(f'Waiting room notification task completed. Sent {notifications_sent} notifications.')
    return f'Sent {notifications_sent} waiting room notifications'


@shared_task
def cleanup_old_events():
    """
    Celery task to mark old events as completed.

    This task should be run periodically (e.g., once per hour).
    """
    now = timezone.now()
    logger.info(f'Running cleanup task at {now}')

    # Find events that have passed their end time but aren't marked as completed
    events = Event.objects.filter(
        status__in=[Event.Status.SCHEDULED, Event.Status.IN_WAITING, Event.Status.IN_PROGRESS],
        end_datetime__lt=now
    )

    updated = events.update(status=Event.Status.COMPLETED)

    logger.info(f'Cleanup task completed. Marked {updated} events as completed.')
    return f'Marked {updated} events as completed'
