import hashlib
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model - read operations."""

    class Meta:
        model = User
        fields = [
            'id',
            'user_code',
            'email',
            'timezone',
            'role',
            'is_active',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'user_code', 'role', 'is_active', 'created_at', 'updated_at']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for normal user registration (generates unique code)."""

    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = ['email', 'password', 'password_confirm', 'timezone']

    def validate(self, attrs):
        """Validate that passwords match."""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                "password": "Password fields didn't match."
            })
        return attrs

    def create(self, validated_data):
        """Create user with auto-generated user_code."""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')

        # Generate unique user_code based on email
        email = validated_data['email']
        user_code = f"user_{hashlib.sha1(email.encode()).hexdigest()[:12]}"

        # Ensure uniqueness
        counter = 1
        original_code = user_code
        while User.objects.filter(user_code=user_code).exists():
            user_code = f"{original_code}_{counter}"
            counter += 1

        user = User.objects.create_user(
            user_code=user_code,
            password=password,
            **validated_data
        )
        return user


class EdxUserRegistrationSerializer(serializers.Serializer):
    """Serializer for edX user registration (uses edX USER_ID)."""

    edx_user_id = serializers.CharField(
        required=True,
        help_text="edX anonymous user ID (will be hashed with SHA-1)"
    )
    email = serializers.EmailField(required=True)
    timezone = serializers.CharField(
        required=False,
        default='UTC',
        help_text="User's timezone (e.g., 'America/Mexico_City')"
    )

    def validate_edx_user_id(self, value):
        """Validate and hash the edX user ID."""
        if not value:
            raise serializers.ValidationError("edX user ID cannot be empty.")

        # Hash the edX user ID with SHA-1 (as specified in requirements)
        hashed_id = hashlib.sha1(value.encode()).hexdigest()
        return hashed_id

    def create(self, validated_data):
        """Create user with edX user_code (hashed)."""
        user_code = validated_data.pop('edx_user_id')

        # Check if user already exists
        user, created = User.objects.get_or_create(
            user_code=user_code,
            defaults={
                'email': validated_data['email'],
                'timezone': validated_data.get('timezone', 'UTC'),
                'role': User.Role.STUDENT
            }
        )

        # If user exists but email/timezone changed, update them
        if not created:
            user.email = validated_data['email']
            user.timezone = validated_data.get('timezone', user.timezone)
            user.save()

        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile."""

    class Meta:
        model = User
        fields = ['email', 'timezone']

    def validate_email(self, value):
        """Ensure email is unique (excluding current user)."""
        user = self.instance
        if User.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise serializers.ValidationError("This email is already in use.")
        return value


class PasswordChangeSerializer(serializers.Serializer):
    """Serializer for changing user password."""

    old_password = serializers.CharField(
        required=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    new_password_confirm = serializers.CharField(
        required=True,
        style={'input_type': 'password'}
    )

    def validate_old_password(self, value):
        """Validate that old password is correct."""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value

    def validate(self, attrs):
        """Validate that new passwords match."""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                "new_password": "New password fields didn't match."
            })
        return attrs

    def save(self):
        """Update user password."""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user
