"""
Celery tasks for event notifications and reminders.
"""
import logging
import time
import os
from datetime import timedelta
from django.utils import timezone
from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.db import transaction

from .models import Event, Enrollment, WaitingRoomParticipant
from apps.meetings.models import Meeting, MeetingParticipant
from apps.meetings.services import distribute_participants, generate_jitsi_url
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
                    time.sleep(float(os.getenv('EMAIL_THROTTLE_DELAY', 0.2)))

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
                    time.sleep(float(os.getenv('EMAIL_THROTTLE_DELAY', 0.2)))

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
                    time.sleep(float(os.getenv('EMAIL_THROTTLE_DELAY', 0.2)))

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


@shared_task
def create_meetings_for_event(event_id):
    """
    Celery task to group waiting participants and create Jitsi meetings.
    """
    logger.info(f'Starting meeting creation for event {event_id}')
    
    try:
        event = Event.objects.get(id=event_id)
    except Event.DoesNotExist:
        logger.error(f'Event {event_id} not found')
        return f'Event {event_id} not found'
        
    # Get active participants
    participants = list(WaitingRoomParticipant.objects.filter(
        event=event,
        status__in=[WaitingRoomParticipant.Status.WAITING, WaitingRoomParticipant.Status.READY]
    ).select_related('user'))
    
    # Try to distribute
    max_per_room = getattr(event.activity, 'max_participants_per_meeting', 6)
    rooms = distribute_participants(participants, max_per_room)
    
    channel_layer = get_channel_layer()
    
    if not rooms:
        logger.warning(f'Event {event_id} completed due to lack of participants (< 2)')
        event.status = Event.Status.COMPLETED
        event.save(update_fields=['status', 'updated_at'])
        
        # Notify whoever is waiting (0 or 1 person)
        async_to_sync(channel_layer.group_send)(
            f'waiting_room_{event.id}',
            {
                'type': 'event_status_update',
                'data': {
                    'type': 'event_status',
                    'status': event.status,
                    'message': 'Event completed due to lack of participants.'
                }
            }
        )
        return f'Event {event_id} completed (not enough participants)'
        
    logger.info(f'Creating {len(rooms)} meetings for event {event_id}')
    
    try:
        with transaction.atomic():
            for i, room_participants in enumerate(rooms):
                group_identifier = f"group-{i+1}"
                jitsi_url = generate_jitsi_url(event.id, group_identifier)
                
                meeting = Meeting.objects.create(
                    event=event,
                    meeting_url=jitsi_url,
                    meeting_provider=Meeting.Provider.JITSI,
                    meeting_id=f'{event.id}-{group_identifier}',
                    start_time=timezone.now()
                )
                
                # Assign participants to this meeting
                MeetingParticipant.objects.bulk_create([
                    MeetingParticipant(
                        meeting=meeting,
                        user=p.user,
                        status=MeetingParticipant.Status.WAITING
                    ) for p in room_participants
                ])
            
            # Event status is already set to IN_PROGRESS by the scanner task
            
    except Exception as e:
        logger.error(f'Failed to create meetings for event {event_id}: {e}')
        # Rollback event status so scanner can retry
        event.status = Event.Status.IN_WAITING
        event.save(update_fields=['status', 'updated_at'])
        return f'Failed to create meetings: {e}'
        
    # Notify waiting room participants that meetings are ready
    async_to_sync(channel_layer.group_send)(
        f'waiting_room_{event.id}',
        {
            'type': 'event_status_update',
            'data': {
                'type': 'event_status',
                'status': event.status,
                'message': 'Meetings are ready!'
            }
        }
    )
    
    return f'Created {len(rooms)} meetings for event {event.id}'


@shared_task
def create_meetings_for_events():
    """
    Scanner task triggered by Celery Beat every minute.
    Looks for IN_WAITING events that have reached their start time,
    marks them IN_PROGRESS (to prevent race conditions) and 
    dispatches the worker task to create their meetings.
    """
    now = timezone.now()
    logger.info(f'Scanning for events that need meetings at {now}')
    
    events = Event.objects.filter(
        status=Event.Status.IN_WAITING,
        start_datetime__lte=now
    )
    
    dispatched = 0
    for event in events:
        event.status = Event.Status.IN_PROGRESS
        event.save(update_fields=['status', 'updated_at'])
        
        create_meetings_for_event.delay(str(event.id))
        dispatched += 1
        
    if dispatched > 0:
        logger.info(f'Dispatched meeting creation for {dispatched} events')
        
    return f'Dispatched {dispatched} events'
