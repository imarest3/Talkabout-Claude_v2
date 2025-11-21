"""
API URL configuration for talkabout project.
"""
from django.urls import path, include

urlpatterns = [
    # User authentication and profile
    path('users/', include('apps.users.urls')),

    # App URLs (will be added in future phases)
    # path('activities/', include('apps.activities.urls')),
    # path('events/', include('apps.events.urls')),
    # path('meetings/', include('apps.meetings.urls')),
]
