from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import User
import hashlib


class UserModelTests(TestCase):
    """Tests for User model."""

    def test_create_user(self):
        """Test creating a normal user."""
        user = User.objects.create_user(
            user_code='test_user_001',
            email='test@example.com',
            password='testpass123',
            timezone='America/Mexico_City'
        )

        self.assertEqual(user.user_code, 'test_user_001')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.timezone, 'America/Mexico_City')
        self.assertEqual(user.role, User.Role.STUDENT)
        self.assertTrue(user.check_password('testpass123'))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)

    def test_create_superuser(self):
        """Test creating a superuser."""
        admin = User.objects.create_superuser(
            user_code='admin_001',
            email='admin@example.com',
            password='adminpass123'
        )

        self.assertEqual(admin.role, User.Role.ADMIN)
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)

    def test_anonymize_user(self):
        """Test anonymizing user data."""
        user = User.objects.create_user(
            user_code='test_user_002',
            email='test2@example.com',
            password='testpass123'
        )

        original_id = user.id
        user.anonymize()

        self.assertIsNone(user.email)
        self.assertEqual(user.user_code, f"anonymous_{original_id}")
        self.assertTrue(user.is_anonymized)
        self.assertFalse(user.is_active)


class AuthenticationAPITests(APITestCase):
    """Tests for authentication endpoints."""

    def setUp(self):
        """Set up test client and create test users."""
        self.client = APIClient()

        # Create a test student
        self.student = User.objects.create_user(
            user_code='student_001',
            email='student@example.com',
            password='studentpass123',
            role=User.Role.STUDENT
        )

        # Create a test teacher
        self.teacher = User.objects.create_user(
            user_code='teacher_001',
            email='teacher@example.com',
            password='teacherpass123',
            role=User.Role.TEACHER
        )

    def test_user_registration(self):
        """Test user registration endpoint."""
        url = reverse('users:register')
        data = {
            'email': 'newuser@example.com',
            'password': 'newpass123!',
            'password_confirm': 'newpass123!',
            'timezone': 'Europe/Madrid'
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('tokens', response.data)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['email'], 'newuser@example.com')

    def test_edx_user_registration(self):
        """Test edX user registration endpoint."""
        url = reverse('users:register_edx')
        edx_user_id = 'test_edx_user_12345'

        data = {
            'edx_user_id': edx_user_id,
            'email': 'edxuser@example.com',
            'timezone': 'America/New_York'
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.data)
        self.assertIn('user', response.data)

        # Verify user_code is hashed
        expected_hash = hashlib.sha1(edx_user_id.encode()).hexdigest()
        self.assertEqual(response.data['user']['user_code'], expected_hash)

    def test_login(self):
        """Test login endpoint."""
        url = reverse('users:login')
        data = {
            'user_code': 'student_001',
            'password': 'studentpass123'
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['user_code'], 'student_001')

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials."""
        url = reverse('users:login')
        data = {
            'user_code': 'student_001',
            'password': 'wrongpassword'
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_refresh(self):
        """Test token refresh endpoint."""
        # First login to get tokens
        login_url = reverse('users:login')
        login_data = {
            'user_code': 'student_001',
            'password': 'studentpass123'
        }
        login_response = self.client.post(login_url, login_data, format='json')
        refresh_token = login_response.data['refresh']

        # Now refresh the token
        refresh_url = reverse('users:token_refresh')
        refresh_data = {'refresh': refresh_token}
        response = self.client.post(refresh_url, refresh_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_get_profile(self):
        """Test getting user profile."""
        # Authenticate
        self.client.force_authenticate(user=self.student)

        url = reverse('users:profile')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user_code'], 'student_001')
        self.assertEqual(response.data['email'], 'student@example.com')

    def test_update_profile(self):
        """Test updating user profile."""
        # Authenticate
        self.client.force_authenticate(user=self.student)

        url = reverse('users:profile_update')
        data = {
            'email': 'newemail@example.com',
            'timezone': 'Asia/Tokyo'
        }

        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'newemail@example.com')
        self.assertEqual(response.data['timezone'], 'Asia/Tokyo')

    def test_change_password(self):
        """Test changing password."""
        # Authenticate
        self.client.force_authenticate(user=self.student)

        url = reverse('users:change_password')
        data = {
            'old_password': 'studentpass123',
            'new_password': 'newsecurepass123!',
            'new_password_confirm': 'newsecurepass123!'
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify new password works
        self.student.refresh_from_db()
        self.assertTrue(self.student.check_password('newsecurepass123!'))

    def test_logout(self):
        """Test logout endpoint."""
        # First login to get tokens
        login_url = reverse('users:login')
        login_data = {
            'user_code': 'student_001',
            'password': 'studentpass123'
        }
        login_response = self.client.post(login_url, login_data, format='json')
        refresh_token = login_response.data['refresh']

        # Authenticate for logout
        self.client.force_authenticate(user=self.student)

        # Logout
        logout_url = reverse('users:logout')
        logout_data = {'refresh_token': refresh_token}
        response = self.client.post(logout_url, logout_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_anonymize_user(self):
        """Test user anonymization."""
        # Authenticate
        self.client.force_authenticate(user=self.student)

        url = reverse('users:anonymize')
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify user is anonymized
        self.student.refresh_from_db()
        self.assertTrue(self.student.is_anonymized)
        self.assertIsNone(self.student.email)
        self.assertIn('anonymous_', self.student.user_code)
