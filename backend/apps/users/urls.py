from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    CustomTokenObtainPairView,
    UserRegistrationView,
    EdxUserRegistrationView,
    logout_view,
    UserProfileView,
    UserProfileUpdateView,
    change_password_view,
    anonymize_user_view,
    unsubscribe_info_view,
    unsubscribe_email_view,
    reactivate_email_view,
    anonymize_by_token_view,
)

app_name = 'users'

urlpatterns = [
    # Authentication
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('auth/logout/', logout_view, name='logout'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Registration
    path('auth/register/', UserRegistrationView.as_view(), name='register'),
    path('auth/register/edx/', EdxUserRegistrationView.as_view(), name='register_edx'),

    # Profile
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('profile/update/', UserProfileUpdateView.as_view(), name='profile_update'),
    path('profile/change-password/', change_password_view, name='change_password'),
    path('profile/anonymize/', anonymize_user_view, name='anonymize'),

    # Token-based unsubscribe (public, no auth — accessible from email links)
    path('unsubscribe/<str:token>/', unsubscribe_info_view, name='unsubscribe_info'),
    path('unsubscribe/<str:token>/email/', unsubscribe_email_view, name='unsubscribe_email'),
    path('unsubscribe/<str:token>/reactivate/', reactivate_email_view, name='reactivate_email'),
    path('unsubscribe/<str:token>/account/', anonymize_by_token_view, name='anonymize_by_token'),
]
