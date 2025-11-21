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
]
