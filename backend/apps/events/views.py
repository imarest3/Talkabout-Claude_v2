from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Event
from .serializers import EventSerializer


class EventViewSet(viewsets.ModelViewSet):
    """API endpoints for managing events."""

    queryset = Event.objects.select_related('activity').all().order_by('start_datetime')
    serializer_class = EventSerializer

    @action(detail=False, methods=['post'], url_path='bulk-create')
    def bulk_create(self, request):
        """Create multiple events at once and return created records."""

        if not isinstance(request.data, list):
            return Response(
                {'detail': 'Expected a list of event objects.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            self.perform_bulk_create(serializer)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_bulk_create(self, serializer):
        serializer.save()
