"""
Email utilities for event notifications.
"""
import logging
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.urls import reverse

logger = logging.getLogger(__name__)


def send_enrollment_confirmation(enrollment):
    """
    Send confirmation email when user enrolls in an event.

    Args:
        enrollment: Enrollment instance
    """
    event = enrollment.event
    user = enrollment.user

    # Build unsubscribe URL
    unsubscribe_url = f"{settings.FRONTEND_URL or 'http://localhost:3000'}/unsubscribe/{enrollment.unsubscribe_token}"

    context = {
        'user': user,
        'event': event,
        'activity': event.activity,
        'unsubscribe_url': unsubscribe_url,
    }

    # Render HTML and plain text versions
    html_message = render_to_string('emails/enrollment_confirmation.html', context)
    plain_message = strip_tags(html_message)

    subject = f'Confirmación de inscripción: {event.activity.title}'

    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email] if user.email else [],
            html_message=html_message,
            fail_silently=False,
        )
        logger.info(f'Enrollment confirmation email sent to {user.user_code} for event {event.id}')
        return True
    except Exception as e:
        logger.error(f'Failed to send enrollment confirmation email: {e}')
        return False


def send_first_reminder(enrollment):
    """
    Send first reminder email before the event.

    Args:
        enrollment: Enrollment instance
    """
    event = enrollment.event
    user = enrollment.user

    unsubscribe_url = f"{settings.FRONTEND_URL or 'http://localhost:3000'}/unsubscribe/{enrollment.unsubscribe_token}"

    context = {
        'user': user,
        'event': event,
        'activity': event.activity,
        'unsubscribe_url': unsubscribe_url,
        'reminder_type': 'first',
    }

    html_message = render_to_string('emails/event_reminder.html', context)
    plain_message = strip_tags(html_message)

    subject = f'Recordatorio: {event.activity.title} - Próximamente'

    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email] if user.email else [],
            html_message=html_message,
            fail_silently=False,
        )
        logger.info(f'First reminder sent to {user.user_code} for event {event.id}')
        return True
    except Exception as e:
        logger.error(f'Failed to send first reminder: {e}')
        return False


def send_second_reminder(enrollment):
    """
    Send second reminder email closer to the event.

    Args:
        enrollment: Enrollment instance
    """
    event = enrollment.event
    user = enrollment.user

    unsubscribe_url = f"{settings.FRONTEND_URL or 'http://localhost:3000'}/unsubscribe/{enrollment.unsubscribe_token}"

    context = {
        'user': user,
        'event': event,
        'activity': event.activity,
        'unsubscribe_url': unsubscribe_url,
        'reminder_type': 'second',
    }

    html_message = render_to_string('emails/event_reminder.html', context)
    plain_message = strip_tags(html_message)

    subject = f'¡Último recordatorio! {event.activity.title} - Hoy'

    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email] if user.email else [],
            html_message=html_message,
            fail_silently=False,
        )
        logger.info(f'Second reminder sent to {user.user_code} for event {event.id}')
        return True
    except Exception as e:
        logger.error(f'Failed to send second reminder: {e}')
        return False


def send_waiting_room_notification(enrollment):
    """
    Send notification when waiting room opens.

    Args:
        enrollment: Enrollment instance
    """
    event = enrollment.event
    user = enrollment.user

    # Build waiting room URL
    waiting_room_url = f"{settings.FRONTEND_URL or 'http://localhost:3000'}/events/{event.id}/waiting-room"
    unsubscribe_url = f"{settings.FRONTEND_URL or 'http://localhost:3000'}/unsubscribe/{enrollment.unsubscribe_token}"

    context = {
        'user': user,
        'event': event,
        'activity': event.activity,
        'waiting_room_url': waiting_room_url,
        'unsubscribe_url': unsubscribe_url,
    }

    html_message = render_to_string('emails/waiting_room_open.html', context)
    plain_message = strip_tags(html_message)

    subject = f'¡Sala de espera abierta! {event.activity.title}'

    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email] if user.email else [],
            html_message=html_message,
            fail_silently=False,
        )
        logger.info(f'Waiting room notification sent to {user.user_code} for event {event.id}')
        return True
    except Exception as e:
        logger.error(f'Failed to send waiting room notification: {e}')
        return False


def send_cancellation_confirmation(enrollment):
    """
    Send confirmation email when user cancels enrollment.

    Args:
        enrollment: Enrollment instance
    """
    event = enrollment.event
    user = enrollment.user

    context = {
        'user': user,
        'event': event,
        'activity': event.activity,
    }

    html_message = render_to_string('emails/cancellation_confirmation.html', context)
    plain_message = strip_tags(html_message)

    subject = f'Cancelación confirmada: {event.activity.title}'

    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email] if user.email else [],
            html_message=html_message,
            fail_silently=False,
        )
        logger.info(f'Cancellation confirmation sent to {user.user_code} for event {event.id}')
        return True
    except Exception as e:
        logger.error(f'Failed to send cancellation confirmation: {e}')
        return False
