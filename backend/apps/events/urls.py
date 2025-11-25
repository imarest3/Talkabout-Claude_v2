from django.urls import path
from .views import (
    EventListView,
    EventCreateView,
    bulk_create_events,
    EventDetailView,
    EventUpdateView,
    EventDeleteView,
    enroll_event,
    unenroll_event,
    MyEnrollmentsView,
    EventEnrollmentsView,
    convert_timezone,
    event_statistics,
)

app_name = 'events'

urlpatterns = [
    # Event CRUD
    path('', EventListView.as_view(), name='event_list'),
    path('create/', EventCreateView.as_view(), name='event_create'),
    path('bulk-create/', bulk_create_events, name='event_bulk_create'),
    path('<uuid:pk>/', EventDetailView.as_view(), name='event_detail'),
    path('<uuid:pk>/update/', EventUpdateView.as_view(), name='event_update'),
    path('<uuid:pk>/delete/', EventDeleteView.as_view(), name='event_delete'),

    # Enrollments
    path('enroll/', enroll_event, name='enroll_event'),
    path('<uuid:event_id>/unenroll/', unenroll_event, name='unenroll_event'),
    path('my-enrollments/', MyEnrollmentsView.as_view(), name='my_enrollments'),
    path('<uuid:pk>/enrollments/', EventEnrollmentsView.as_view(), name='event_enrollments'),

    # Utilities
    path('convert-timezone/', convert_timezone, name='convert_timezone'),
    path('<uuid:pk>/statistics/', event_statistics, name='event_statistics'),
]
