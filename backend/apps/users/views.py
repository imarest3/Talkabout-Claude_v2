from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User
from .serializers import (
    UserSerializer,
    UserRegistrationSerializer,
    EdxUserRegistrationSerializer,
    UserUpdateSerializer,
    PasswordChangeSerializer
)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom JWT serializer to include user data in response."""

    def validate(self, attrs):
        data = super().validate(attrs)

        # Add custom user data to response
        data['user'] = {
            'id': str(self.user.id),
            'user_code': self.user.user_code,
            'email': self.user.email,
            'role': self.user.role,
            'timezone': self.user.timezone,
        }

        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom login view that returns user data along with tokens."""
    serializer_class = CustomTokenObtainPairSerializer


class UserRegistrationView(generics.CreateAPIView):
    """
    Register a new user with auto-generated user_code.
    For normal registration (not from edX).
    """
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate tokens for the new user
        refresh = RefreshToken.for_user(user)

        return Response({
            'message': 'User registered successfully',
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)


class EdxUserRegistrationView(generics.CreateAPIView):
    """
    Register or get a user from edX.
    Uses edX USER_ID (hashed with SHA-1) as user_code.
    """
    serializer_class = EdxUserRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate tokens for the user
        refresh = RefreshToken.for_user(user)

        return Response({
            'message': 'User registered/retrieved successfully',
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    Logout view that blacklists the refresh token.
    """
    try:
        refresh_token = request.data.get('refresh_token')
        if not refresh_token:
            return Response(
                {'error': 'Refresh token is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        token = RefreshToken(refresh_token)
        token.blacklist()

        return Response({
            'message': 'Successfully logged out'
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


class UserProfileView(generics.RetrieveAPIView):
    """Get current user profile."""
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserProfileUpdateView(generics.UpdateAPIView):
    """Update current user profile (email, timezone)."""
    serializer_class = UserUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password_view(request):
    """Change user password."""
    serializer = PasswordChangeSerializer(
        data=request.data,
        context={'request': request}
    )

    if serializer.is_valid():
        serializer.save()
        return Response({
            'message': 'Password changed successfully'
        }, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def anonymize_user_view(request):
    """
    Anonymize user data (GDPR compliance).
    Removes email and user_code, keeps statistics.
    """
    user = request.user

    if user.is_anonymized:
        return Response({
            'error': 'User is already anonymized'
        }, status=status.HTTP_400_BAD_REQUEST)

    user.anonymize()

    return Response({
        'message': 'User data anonymized successfully. You have been logged out.'
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def unsubscribe_info_view(request, token):
    """Return masked user info for the unsubscribe page (public, no auth)."""
    try:
        user = User.objects.get(unsubscribe_token=token)
    except User.DoesNotExist:
        return Response({'error': 'Token inválido o caducado.'}, status=status.HTTP_404_NOT_FOUND)

    if user.is_anonymized:
        return Response({'error': 'Esta cuenta ya ha sido dada de baja.'}, status=status.HTTP_400_BAD_REQUEST)

    email = user.email or ''
    if email and '@' in email:
        local, domain = email.split('@', 1)
        masked = local[:2] + '***@' + domain
    else:
        masked = '(sin correo)'

    return Response({
        'email_masked': masked,
        'email_notifications_enabled': user.email_notifications_enabled,
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def unsubscribe_email_view(request, token):
    """Disable email notifications by token (public, no auth)."""
    try:
        user = User.objects.get(unsubscribe_token=token)
    except User.DoesNotExist:
        return Response({'error': 'Token inválido o caducado.'}, status=status.HTTP_404_NOT_FOUND)

    if user.is_anonymized:
        return Response({'error': 'Esta cuenta ya ha sido dada de baja.'}, status=status.HTTP_400_BAD_REQUEST)

    user.email_notifications_enabled = False
    user.save(update_fields=['email_notifications_enabled'])
    return Response({'message': 'Has sido dado de baja del envío de correos correctamente.'})


@api_view(['POST'])
@permission_classes([AllowAny])
def reactivate_email_view(request, token):
    """Re-enable email notifications by token (public, no auth)."""
    try:
        user = User.objects.get(unsubscribe_token=token)
    except User.DoesNotExist:
        return Response({'error': 'Token inválido o caducado.'}, status=status.HTTP_404_NOT_FOUND)

    if user.is_anonymized:
        return Response({'error': 'Esta cuenta ya ha sido dada de baja.'}, status=status.HTTP_400_BAD_REQUEST)

    user.email_notifications_enabled = True
    user.save(update_fields=['email_notifications_enabled'])
    return Response({'message': 'Notificaciones por correo reactivadas correctamente.'})


@api_view(['POST'])
@permission_classes([AllowAny])
def anonymize_by_token_view(request, token):
    """Permanently anonymize a user account by token (public, no auth)."""
    try:
        user = User.objects.get(unsubscribe_token=token)
    except User.DoesNotExist:
        return Response({'error': 'Token inválido o caducado.'}, status=status.HTTP_404_NOT_FOUND)

    if user.is_anonymized:
        return Response({'error': 'Esta cuenta ya ha sido dada de baja definitivamente.'}, status=status.HTTP_400_BAD_REQUEST)

    user.anonymize()
    return Response({'message': 'Cuenta eliminada definitivamente. Tus datos han sido anonimizados.'})
