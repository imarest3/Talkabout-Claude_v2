from rest_framework import generics, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count
from django.utils import timezone as django_timezone
from django_filters.rest_framework import DjangoFilterBackend
from datetime import datetime, timedelta
import pytz

from .models import Event, Enrollment
from .serializers import (
    EventSerializer,
    EventCreateSerializer,
    EventBulkCreateSerializer,
    EventUpdateSerializer,
    EnrollmentSerializer,
    EnrollmentCreateSerializer,
    TimezoneConversionSerializer
)
from apps.users.permissions import IsTeacherOrAdmin
from apps.activities.models import Activity


class EventListView(generics.ListCreateAPIView):
    """
    List all events (GET) or create a single event (POST).
    - GET: Available to all authenticated users.
    - POST: Only teachers and admins can create events.
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'activity']
    search_fields = ['activity__code', 'activity__title']
    ordering_fields = ['start_datetime', 'created_at']
    ordering = ['start_datetime']

    def get_serializer_class(self):
        """Use different serializers for list and create."""
        if self.request.method == 'POST':
            return EventCreateSerializer
        return EventSerializer

    def get_permissions(self):
        """Only teachers and admins can create events."""
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsTeacherOrAdmin()]
        return [IsAuthenticated()]

    def get_queryset(self):
        """Get events with enrollment counts."""
        queryset = Event.objects.select_related('activity').annotate(
            enrolled_count=Count('enrollments', filter=Q(enrollments__status='enrolled')),
            attended_count=Count('enrollments', filter=Q(enrollments__status='attended'))
        )

        # Filter by activity code if provided
        activity_code = self.request.query_params.get('activity_code')
        if activity_code:
            queryset = queryset.filter(activity__code=activity_code)

        # Filter by date range if provided
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date)
                queryset = queryset.filter(start_datetime__gte=start_dt)
            except ValueError:
                pass

        if end_date:
            try:
                end_dt = datetime.fromisoformat(end_date)
                queryset = queryset.filter(start_datetime__lte=end_dt)
            except ValueError:
                pass

        return queryset


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def bulk_create_events(request):
    """
    Create multiple events based on date range and hours.
    Only teachers and admins can create events.
    """
    serializer = EventBulkCreateSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data
    activity = data['activity_code']
    start_date = data['start_date']
    end_date = data['end_date']
    hours_utc = data['hours_utc']
    duration_minutes = data['duration_minutes']
    waiting_time_minutes = data['waiting_time_minutes']
    first_reminder_minutes = data.get('first_reminder_minutes')
    second_reminder_minutes = data.get('second_reminder_minutes')

    # Generate events
    events_created = []
    current_date = start_date

    while current_date <= end_date:
        for hour_str in hours_utc:
            # Parse hour
            hour_time = datetime.strptime(hour_str, '%H:%M').time()

            # Create datetime in UTC
            start_datetime = datetime.combine(current_date, hour_time)
            start_datetime = pytz.UTC.localize(start_datetime)
            end_datetime = start_datetime + timedelta(minutes=duration_minutes)

            # Skip if in the past
            if start_datetime <= django_timezone.now():
                continue

            # Create event
            event = Event.objects.create(
                activity=activity,
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                waiting_time_minutes=waiting_time_minutes,
                first_reminder_minutes=first_reminder_minutes,
                second_reminder_minutes=second_reminder_minutes
            )
            events_created.append(event)

        current_date += timedelta(days=1)

    # Serialize and return
    serializer = EventSerializer(events_created, many=True)

    return Response({
        'message': f'Successfully created {len(events_created)} events',
        'events': serializer.data
    }, status=status.HTTP_201_CREATED)


class EventDetailView(generics.RetrieveAPIView):
    """
    Get details of a specific event.
    Available to all authenticated users.
    """
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]
    queryset = Event.objects.select_related('activity').annotate(
        enrolled_count=Count('enrollments', filter=Q(enrollments__status='enrolled')),
        attended_count=Count('enrollments', filter=Q(enrollments__status='attended'))
    )


class EventUpdateView(generics.UpdateAPIView):
    """
    Update an event.
    Only teachers and admins can update events.
    """
    serializer_class = EventUpdateSerializer
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]
    queryset = Event.objects.all()


class EventDeleteView(generics.DestroyAPIView):
    """
    Delete an event.
    Only teachers and admins can delete events.
    Cannot delete events with enrollments.
    """
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]
    queryset = Event.objects.all()

    def destroy(self, request, *args, **kwargs):
        """Check if event has enrollments before deleting."""
        instance = self.get_object()

        # Check if event has enrollments
        if instance.enrollments.exists():
            return Response({
                'error': 'Cannot delete events with enrollments. Cancel the event instead.'
            }, status=status.HTTP_400_BAD_REQUEST)

        instance.delete()
        return Response({
            'message': 'Event deleted successfully'
        }, status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def enroll_event(request):
    """
    Enroll current user in an event.
    """
    serializer = EnrollmentCreateSerializer(data=request.data, context={'request': request})

    if serializer.is_valid():
        enrollment = serializer.save()
        return Response(
            EnrollmentSerializer(enrollment).data,
            status=status.HTTP_201_CREATED
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def unenroll_event(request, event_id):
    """
    Unenroll current user from an event.
    """
    event = get_object_or_404(Event, id=event_id)
    user = request.user

    # Get enrollment
    try:
        enrollment = Enrollment.objects.get(user=user, event=event)
    except Enrollment.DoesNotExist:
        return Response({
            'error': 'You are not enrolled in this event'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Check if event hasn't started yet
    if event.start_datetime <= django_timezone.now():
        return Response({
            'error': 'Cannot unenroll from events that have already started'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Cancel enrollment
    enrollment.cancel()

    return Response({
        'message': 'Successfully unenrolled from event'
    }, status=status.HTTP_200_OK)


class MyEnrollmentsView(generics.ListAPIView):
    """
    List current user's enrollments.
    """
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Get enrollments for current user."""
        return Enrollment.objects.filter(
            user=self.request.user
        ).select_related('event', 'event__activity', 'user').order_by('-enrolled_at')


class EventEnrollmentsView(generics.ListAPIView):
    """
    List enrollments for a specific event.
    Only teachers and admins can view enrollments.
    """
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]

    def get_queryset(self):
        """Get enrollments for specific event."""
        event_id = self.kwargs['pk']
        return Enrollment.objects.filter(
            event_id=event_id
        ).select_related('event', 'event__activity', 'user').order_by('-enrolled_at')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def convert_timezone(request):
    """
    Convert a UTC datetime to a target timezone.
    Useful for displaying event times in user's local timezone.
    """
    serializer = TimezoneConversionSerializer(data=request.data)

    if serializer.is_valid():
        result = serializer.to_representation(serializer.validated_data)
        return Response(result, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def event_statistics(request, pk):
    """
    Get statistics for a specific event.
    """
    event = get_object_or_404(Event, pk=pk)

    enrollments = event.enrollments.all()
    total_enrolled = enrollments.filter(status=Enrollment.Status.ENROLLED).count()
    total_cancelled = enrollments.filter(status=Enrollment.Status.CANCELLED).count()
    total_attended = enrollments.filter(status=Enrollment.Status.ATTENDED).count()
    total_no_show = enrollments.filter(status=Enrollment.Status.NO_SHOW).count()

    return Response({
        'event_id': str(event.id),
        'activity_code': event.activity.code,
        'activity_title': event.activity.title,
        'start_datetime': event.start_datetime,
        'end_datetime': event.end_datetime,
        'status': event.status,
        'total_enrolled': total_enrolled,
        'total_cancelled': total_cancelled,
        'total_attended': total_attended,
        'total_no_show': total_no_show,
        'max_participants_per_meeting': event.activity.max_participants_per_meeting,
        'meetings_count': event.meetings.count()
    }, status=status.HTTP_200_OK)
