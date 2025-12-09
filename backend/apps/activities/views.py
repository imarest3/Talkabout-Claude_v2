from rest_framework import generics, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import models
from django_filters.rest_framework import DjangoFilterBackend

from .models import Activity, ActivityFile
from .serializers import (
    ActivitySerializer,
    ActivityCreateUpdateSerializer,
    ActivityFileSerializer,
    ActivityFileUploadSerializer
)
from apps.users.permissions import IsTeacherOrAdmin, IsTeacherOrAdminOrReadOnly


class ActivityListView(generics.ListAPIView):
    """
    List all activities with filtering and search.
    Available to all authenticated users.
    """
    serializer_class = ActivitySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'created_by']
    search_fields = ['code', 'title', 'description']
    ordering_fields = ['created_at', 'title', 'code']
    ordering = ['-created_at']

    def get_queryset(self):
        """
        Get queryset based on user role.
        - Students see only active activities
        - Teachers see their own activities + active ones
        - Admins see all activities
        """
        user = self.request.user
        queryset = Activity.objects.select_related('created_by').prefetch_related('files')

        if user.role == 'student':
            # Students only see active activities
            queryset = queryset.filter(is_active=True)
        elif user.role == 'teacher':
            # Teachers see their own activities or active ones
            queryset = queryset.filter(
                models.Q(created_by=user) | models.Q(is_active=True)
            )
        # Admins see everything (no filter)

        return queryset


class ActivityCreateView(generics.CreateAPIView):
    """
    Create a new activity.
    Only teachers and admins can create activities.
    """
    serializer_class = ActivityCreateUpdateSerializer
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]

    def perform_create(self, serializer):
        """Set created_by to current user."""
        serializer.save(created_by=self.request.user)


class ActivityDetailView(generics.RetrieveAPIView):
    """
    Get details of a specific activity.
    Available to all authenticated users.
    """
    serializer_class = ActivitySerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'code'

    def get_queryset(self):
        """Apply same visibility rules as list view."""
        user = self.request.user
        queryset = Activity.objects.select_related('created_by').prefetch_related('files')

        if user.role == 'student':
            queryset = queryset.filter(is_active=True)
        elif user.role == 'teacher':
            queryset = queryset.filter(
                models.Q(created_by=user) | models.Q(is_active=True)
            )

        return queryset


class ActivityUpdateView(generics.UpdateAPIView):
    """
    Update an activity.
    Only the creator or admins can update.
    """
    serializer_class = ActivityCreateUpdateSerializer
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]
    lookup_field = 'code'
    queryset = Activity.objects.all()

    def check_object_permissions(self, request, obj):
        """Check if user can update this activity."""
        super().check_object_permissions(request, obj)

        # Only creator or admin can update
        if request.user.role != 'admin' and obj.created_by != request.user:
            self.permission_denied(
                request,
                message="You don't have permission to update this activity."
            )


class ActivityDeleteView(generics.DestroyAPIView):
    """
    Delete an activity.
    Only the creator or admins can delete.
    """
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]
    lookup_field = 'code'
    queryset = Activity.objects.all()

    def check_object_permissions(self, request, obj):
        """Check if user can delete this activity."""
        super().check_object_permissions(request, obj)

        # Only creator or admin can delete
        if request.user.role != 'admin' and obj.created_by != request.user:
            self.permission_denied(
                request,
                message="You don't have permission to delete this activity."
            )

    def destroy(self, request, *args, **kwargs):
        """Soft delete: mark as inactive instead of deleting."""
        instance = self.get_object()

        # Check if activity has events
        if instance.events.exists():
            # Soft delete: mark as inactive
            instance.is_active = False
            instance.save()
            return Response({
                'message': 'Activity marked as inactive (has associated events)'
            }, status=status.HTTP_200_OK)
        else:
            # Hard delete if no events
            instance.delete()
            return Response({
                'message': 'Activity deleted successfully'
            }, status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def upload_activity_file(request, code):
    """
    Upload a file to an activity.
    Only the creator or admins can upload files.
    """
    activity = get_object_or_404(Activity, code=code)

    # Check permissions
    if request.user.role != 'admin' and activity.created_by != request.user:
        return Response({
            'error': "You don't have permission to upload files to this activity."
        }, status=status.HTTP_403_FORBIDDEN)

    serializer = ActivityFileUploadSerializer(
        data=request.data,
        context={'activity': activity, 'request': request}
    )

    if serializer.is_valid():
        file_instance = serializer.save()
        return Response(
            ActivityFileSerializer(file_instance, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def delete_activity_file(request, code, file_id):
    """
    Delete a file from an activity.
    Only the creator or admins can delete files.
    """
    activity = get_object_or_404(Activity, code=code)
    file_instance = get_object_or_404(ActivityFile, id=file_id, activity=activity)

    # Check permissions
    if request.user.role != 'admin' and activity.created_by != request.user:
        return Response({
            'error': "You don't have permission to delete files from this activity."
        }, status=status.HTTP_403_FORBIDDEN)

    # Delete the actual file from storage
    if file_instance.file:
        file_instance.file.delete(save=False)

    file_instance.delete()

    return Response({
        'message': 'File deleted successfully'
    }, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def activity_statistics(request, code):
    """
    Get statistics for an activity.
    Shows event count, total enrollments, etc.
    """
    activity = get_object_or_404(Activity, code=code)

    # Check visibility
    user = request.user
    if user.role == 'student' and not activity.is_active:
        return Response({
            'error': 'Activity not found'
        }, status=status.HTTP_404_NOT_FOUND)
    elif user.role == 'teacher' and not activity.is_active and activity.created_by != user:
        return Response({
            'error': 'Activity not found'
        }, status=status.HTTP_404_NOT_FOUND)

    # Calculate statistics using aggregations (more efficient)
    from django.db.models import Count, Q
    from apps.events.models import Enrollment

    event_stats = activity.events.aggregate(
        total_events=Count('id'),
        active_events=Count('id', filter=Q(status='scheduled')),
        completed_events=Count('id', filter=Q(status='completed'))
    )

    enrollment_stats = Enrollment.objects.filter(
        event__activity=activity
    ).aggregate(
        total_enrollments=Count('id'),
        enrolled_count=Count('id', filter=Q(status='enrolled')),
        attended_count=Count('id', filter=Q(status='attended'))
    )

    total_enrollments = enrollment_stats['total_enrollments']
    attended_count = enrollment_stats['attended_count']

    return Response({
        'activity_code': activity.code,
        'activity_title': activity.title,
        'total_events': event_stats['total_events'],
        'active_events': event_stats['active_events'],
        'completed_events': event_stats['completed_events'],
        'total_enrollments': total_enrollments,
        'currently_enrolled': enrollment_stats['enrolled_count'],
        'total_attended': attended_count,
        'attendance_rate': (
            round((attended_count / total_enrollments * 100), 2)
            if total_enrollments > 0 else 0
        )
    }, status=status.HTTP_200_OK)
