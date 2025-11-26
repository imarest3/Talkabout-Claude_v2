"""
API URL configuration for talkabout project.
"""
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    # JWT Authentication
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # App URLs (will be added in future phases)
    # path('users/', include('apps.users.urls')),
    # path('activities/', include('apps.activities.urls')),
    path('events/', include('apps.events.urls')),
    # path('meetings/', include('apps.meetings.urls')),
]
