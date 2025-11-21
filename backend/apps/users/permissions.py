from rest_framework import permissions
from .models import User


class IsAdmin(permissions.BasePermission):
    """
    Permission to check if user is an administrator.
    """

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == User.Role.ADMIN
        )


class IsTeacherOrAdmin(permissions.BasePermission):
    """
    Permission to check if user is a teacher or administrator.
    """

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role in [User.Role.TEACHER, User.Role.ADMIN]
        )


class IsStudent(permissions.BasePermission):
    """
    Permission to check if user is a student.
    """

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == User.Role.STUDENT
        )


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission to check if user is the owner of the object or an administrator.
    Object must have a 'user' attribute.
    """

    def has_object_permission(self, request, view, obj):
        # Admin can access any object
        if request.user.role == User.Role.ADMIN:
            return True

        # Check if user owns the object
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'created_by'):
            return obj.created_by == request.user

        return False


class IsTeacherOrAdminOrReadOnly(permissions.BasePermission):
    """
    Permission that allows:
    - Teachers and Admins: full access
    - Students: read-only access
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Read permissions for any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions only for teacher or admin
        return request.user.role in [User.Role.TEACHER, User.Role.ADMIN]
