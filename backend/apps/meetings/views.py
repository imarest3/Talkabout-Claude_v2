from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, PermissionDenied
from django.shortcuts import get_object_or_404

from apps.events.models import Event
from .models import Meeting, MeetingParticipant
from .serializers import MeetingSerializer


class MyMeetingRetrieveView(generics.RetrieveAPIView):
    """
    API view to retrieve the specific meeting assigned to the authenticated user for a given event.
    """
    serializer_class = MeetingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        event_id = self.kwargs.get('event_id')
        user = self.request.user

        # Verify the event exists
        event = get_object_or_404(Event, id=event_id)

        # Ensure the event has reached a state where meetings exist
        if event.status not in [Event.Status.IN_PROGRESS, Event.Status.COMPLETED]:
            raise PermissionDenied("Meetings for this event have not been generated yet or the event is already over.")

        # Find the specific meeting participant record for this user and event
        try:
            participant = MeetingParticipant.objects.select_related('meeting').get(
                user=user,
                meeting__event=event
            )
            return participant.meeting
        except MeetingParticipant.DoesNotExist:
            raise NotFound("You are not assigned to any meeting for this event. (You may not have been in the waiting room).")
