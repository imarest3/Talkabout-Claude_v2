import uuid
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils.timezone import now as timezone_now


class UserManager(BaseUserManager):
    """Custom user manager for User model."""

    def create_user(self, user_code, email=None, password=None, **extra_fields):
        """Create and save a regular user."""
        if not user_code:
            raise ValueError('The user_code field must be set')

        if email:
            email = self.normalize_email(email)

        user = self.model(user_code=user_code, email=email, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, user_code, email, password=None, **extra_fields):
        """Create and save a superuser."""
        extra_fields.setdefault('role', User.Role.ADMIN)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(user_code, email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model for Talkabout application."""

    class Role(models.TextChoices):
        ADMIN = 'admin', 'Administrator'
        TEACHER = 'teacher', 'Teacher'
        STUDENT = 'student', 'Student'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_code = models.CharField(max_length=255, unique=True, db_index=True)
    email = models.EmailField(max_length=255, null=True, blank=True, unique=True)
    timezone = models.CharField(max_length=100, default='UTC')
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.STUDENT
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_anonymized = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone_now)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'user_code'
    REQUIRED_FIELDS = ['email']

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user_code} ({self.get_role_display()})"

    def anonymize(self):
        """Anonymize user data when they unsubscribe."""
        self.email = None
        self.user_code = f"anonymous_{self.id}"
        self.is_anonymized = True
        self.is_active = False
        self.save()
