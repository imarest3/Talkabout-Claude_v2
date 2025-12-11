"""
WebSocket consumer for waiting room functionality.
"""
import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone

logger = logging.getLogger(__name__)


class WaitingRoomConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for event waiting rooms.

    Handles:
    - User connections/disconnections
    - Real-time participant list updates
    - Waiting room status broadcast
    """

    async def connect(self):
        """Handle WebSocket connection."""
        self.event_id = self.scope['url_route']['kwargs']['event_id']
        self.room_group_name = f'waiting_room_{self.event_id}'
        self.user = self.scope['user']

        # Check if user is authenticated
        if not self.user.is_authenticated:
            logger.warning('Unauthenticated user attempted to connect to waiting room')
            await self.close()
            return

        # Check if user is enrolled in this event
        is_enrolled = await self.check_enrollment()
        if not is_enrolled:
            logger.warning(f'User {self.user.user_code} not enrolled in event {self.event_id}')
            await self.close()
            return

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # Add user to waiting room
        await self.add_participant()

        # Broadcast updated participant list
        await self.broadcast_participant_list()

        logger.info(f'User {self.user.user_code} connected to waiting room for event {self.event_id}')

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        # Mark participant as disconnected
        await self.remove_participant()

        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        # Broadcast updated participant list
        await self.broadcast_participant_list()

        logger.info(f'User {self.user.user_code} disconnected from waiting room for event {self.event_id}')

    async def receive(self, text_data):
        """
        Handle messages from WebSocket.

        Expected message types:
        - ping: Keep-alive heartbeat
        - ready: User indicates they're ready
        """
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            if message_type == 'ping':
                # Update last seen timestamp
                await self.update_last_seen()
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'timestamp': timezone.now().isoformat()
                }))

            elif message_type == 'ready':
                # Mark user as ready
                await self.mark_ready()
                await self.broadcast_participant_list()

        except json.JSONDecodeError:
            logger.error('Invalid JSON received in waiting room')
        except Exception as e:
            logger.error(f'Error processing waiting room message: {e}')

    async def participant_list_update(self, event):
        """
        Handle participant list update broadcasts.

        Args:
            event: Event data from channel layer
        """
        await self.send(text_data=json.dumps(event['data']))

    async def event_status_update(self, event):
        """
        Handle event status update broadcasts.

        Args:
            event: Event data from channel layer
        """
        await self.send(text_data=json.dumps(event['data']))

    async def broadcast_participant_list(self):
        """Broadcast current participant list to all connected users."""
        participants = await self.get_participants()

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'participant_list_update',
                'data': {
                    'type': 'participant_list',
                    'participants': participants,
                    'count': len(participants)
                }
            }
        )

    @database_sync_to_async
    def check_enrollment(self):
        """Check if user is enrolled in the event."""
        from .models import Enrollment, Event

        try:
            event = Event.objects.get(id=self.event_id)
            enrollment = Enrollment.objects.get(
                event=event,
                user=self.user,
                status=Enrollment.Status.ENROLLED
            )
            return True
        except (Event.DoesNotExist, Enrollment.DoesNotExist):
            return False

    @database_sync_to_async
    def add_participant(self):
        """Add user to waiting room participants."""
        from .models import WaitingRoomParticipant, Event, Enrollment

        event = Event.objects.get(id=self.event_id)
        enrollment = Enrollment.objects.get(event=event, user=self.user)

        participant, created = WaitingRoomParticipant.objects.update_or_create(
            event=event,
            user=self.user,
            defaults={
                'enrollment': enrollment,
                'status': WaitingRoomParticipant.Status.WAITING,
                'connection_id': self.channel_name,
                'last_seen': timezone.now()
            }
        )

        return participant

    @database_sync_to_async
    def remove_participant(self):
        """Mark participant as disconnected."""
        from .models import WaitingRoomParticipant

        try:
            participant = WaitingRoomParticipant.objects.get(
                event_id=self.event_id,
                user=self.user
            )
            participant.mark_disconnected()
        except WaitingRoomParticipant.DoesNotExist:
            pass

    @database_sync_to_async
    def update_last_seen(self):
        """Update participant's last seen timestamp."""
        from .models import WaitingRoomParticipant

        try:
            participant = WaitingRoomParticipant.objects.get(
                event_id=self.event_id,
                user=self.user
            )
            participant.update_last_seen()
        except WaitingRoomParticipant.DoesNotExist:
            pass

    @database_sync_to_async
    def mark_ready(self):
        """Mark participant as ready."""
        from .models import WaitingRoomParticipant

        try:
            participant = WaitingRoomParticipant.objects.get(
                event_id=self.event_id,
                user=self.user
            )
            participant.mark_ready()
        except WaitingRoomParticipant.DoesNotExist:
            pass

    @database_sync_to_async
    def get_participants(self):
        """Get list of current waiting room participants."""
        from .models import WaitingRoomParticipant

        participants = WaitingRoomParticipant.objects.filter(
            event_id=self.event_id,
            status__in=[WaitingRoomParticipant.Status.WAITING, WaitingRoomParticipant.Status.READY]
        ).select_related('user').order_by('joined_at')

        return [
            {
                'user_code': p.user.user_code,
                'joined_at': p.joined_at.isoformat(),
                'status': p.status,
                'is_ready': p.status == WaitingRoomParticipant.Status.READY
            }
            for p in participants
        ]
