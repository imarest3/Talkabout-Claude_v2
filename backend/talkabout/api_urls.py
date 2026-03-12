"""
API URL configuration for talkabout project.
"""
from django.urls import path, include

urlpatterns = [
    # User authentication and profile
    path('users/', include('apps.users.urls')),

    # Activities
    path('activities/', include('apps.activities.urls')),

    # Events
    path('events/', include('apps.events.urls')),
]
