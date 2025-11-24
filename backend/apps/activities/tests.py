from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from apps.users.models import User
from .models import Activity, ActivityFile


class ActivityModelTests(TestCase):
    """Tests for Activity model."""

    def setUp(self):
        """Set up test data."""
        self.teacher = User.objects.create_user(
            user_code='teacher_001',
            email='teacher@example.com',
            password='teacherpass123',
            role=User.Role.TEACHER
        )

    def test_create_activity(self):
        """Test creating an activity."""
        activity = Activity.objects.create(
            code='ACT001',
            title='Test Activity',
            description='<p>Test description</p>',
            max_participants_per_meeting=6,
            created_by=self.teacher
        )

        self.assertEqual(activity.code, 'ACT001')
        self.assertEqual(activity.title, 'Test Activity')
        self.assertEqual(activity.max_participants_per_meeting, 6)
        self.assertTrue(activity.is_active)
        self.assertEqual(activity.created_by, self.teacher)

    def test_activity_str(self):
        """Test activity string representation."""
        activity = Activity.objects.create(
            code='ACT002',
            title='Another Activity',
            description='Description',
            created_by=self.teacher
        )

        self.assertEqual(str(activity), 'ACT002: Another Activity')


class ActivityAPITests(APITestCase):
    """Tests for Activity API endpoints."""

    def setUp(self):
        """Set up test data and clients."""
        self.client = APIClient()

        # Create users
        self.admin = User.objects.create_user(
            user_code='admin_001',
            email='admin@example.com',
            password='adminpass123',
            role=User.Role.ADMIN
        )

        self.teacher = User.objects.create_user(
            user_code='teacher_001',
            email='teacher@example.com',
            password='teacherpass123',
            role=User.Role.TEACHER
        )

        self.student = User.objects.create_user(
            user_code='student_001',
            email='student@example.com',
            password='studentpass123',
            role=User.Role.STUDENT
        )

        # Create test activities
        self.activity1 = Activity.objects.create(
            code='ACT001',
            title='Active Activity',
            description='<p>Active activity description</p>',
            max_participants_per_meeting=6,
            created_by=self.teacher,
            is_active=True
        )

        self.activity2 = Activity.objects.create(
            code='ACT002',
            title='Inactive Activity',
            description='<p>Inactive activity description</p>',
            max_participants_per_meeting=4,
            created_by=self.teacher,
            is_active=False
        )

    def test_list_activities_as_student(self):
        """Test listing activities as a student (only sees active)."""
        self.client.force_authenticate(user=self.student)

        url = reverse('activities:activity_list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['code'], 'ACT001')

    def test_list_activities_as_teacher(self):
        """Test listing activities as a teacher (sees own + active)."""
        self.client.force_authenticate(user=self.teacher)

        url = reverse('activities:activity_list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_list_activities_as_admin(self):
        """Test listing activities as admin (sees all)."""
        self.client.force_authenticate(user=self.admin)

        url = reverse('activities:activity_list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_create_activity_as_teacher(self):
        """Test creating an activity as a teacher."""
        self.client.force_authenticate(user=self.teacher)

        url = reverse('activities:activity_create')
        data = {
            'code': 'ACT003',
            'title': 'New Activity',
            'description': '<p>New activity description</p>',
            'max_participants_per_meeting': 8,
            'is_active': True
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['code'], 'ACT003')
        self.assertTrue(Activity.objects.filter(code='ACT003').exists())

    def test_create_activity_as_student_fails(self):
        """Test that students cannot create activities."""
        self.client.force_authenticate(user=self.student)

        url = reverse('activities:activity_create')
        data = {
            'code': 'ACT004',
            'title': 'Student Activity',
            'description': '<p>Should fail</p>',
            'max_participants_per_meeting': 6
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_activity_detail(self):
        """Test getting activity details."""
        self.client.force_authenticate(user=self.student)

        url = reverse('activities:activity_detail', kwargs={'code': 'ACT001'})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 'ACT001')
        self.assertEqual(response.data['title'], 'Active Activity')

    def test_update_activity_as_creator(self):
        """Test updating activity as the creator."""
        self.client.force_authenticate(user=self.teacher)

        url = reverse('activities:activity_update', kwargs={'code': 'ACT001'})
        data = {
            'title': 'Updated Activity Title',
            'description': '<p>Updated description</p>',
            'max_participants_per_meeting': 10,
            'is_active': True,
            'code': 'ACT001'
        }

        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Activity Title')

        # Verify in database
        self.activity1.refresh_from_db()
        self.assertEqual(self.activity1.title, 'Updated Activity Title')

    def test_update_activity_as_non_creator_fails(self):
        """Test that non-creators cannot update activities."""
        another_teacher = User.objects.create_user(
            user_code='teacher_002',
            email='teacher2@example.com',
            password='teacherpass123',
            role=User.Role.TEACHER
        )
        self.client.force_authenticate(user=another_teacher)

        url = reverse('activities:activity_update', kwargs={'code': 'ACT001'})
        data = {
            'title': 'Hacked Title',
            'code': 'ACT001'
        }

        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_activity_without_events(self):
        """Test hard deleting activity when it has no events."""
        self.client.force_authenticate(user=self.teacher)

        url = reverse('activities:activity_delete', kwargs={'code': 'ACT002'})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Activity.objects.filter(code='ACT002').exists())

    def test_search_activities(self):
        """Test searching activities by title."""
        self.client.force_authenticate(user=self.teacher)

        url = reverse('activities:activity_list')
        response = self.client.get(url, {'search': 'Active'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)

    def test_filter_activities_by_active_status(self):
        """Test filtering activities by is_active status."""
        self.client.force_authenticate(user=self.teacher)

        url = reverse('activities:activity_list')
        response = self.client.get(url, {'is_active': 'true'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for activity in response.data['results']:
            self.assertTrue(activity['is_active'])


class ActivityFileAPITests(APITestCase):
    """Tests for Activity File API endpoints."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()

        self.teacher = User.objects.create_user(
            user_code='teacher_001',
            email='teacher@example.com',
            password='teacherpass123',
            role=User.Role.TEACHER
        )

        self.activity = Activity.objects.create(
            code='ACT001',
            title='Test Activity',
            description='<p>Description</p>',
            max_participants_per_meeting=6,
            created_by=self.teacher
        )

    def test_upload_file_to_activity(self):
        """Test uploading a file to an activity."""
        self.client.force_authenticate(user=self.teacher)

        url = reverse('activities:upload_file', kwargs={'code': 'ACT001'})

        # Create a test file
        test_file = SimpleUploadedFile(
            "test_document.txt",
            b"This is a test file content.",
            content_type="text/plain"
        )

        data = {
            'file': test_file,
            'filename': 'Test Document'
        }

        response = self.client.post(url, data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['filename'], 'Test Document')
        self.assertTrue(ActivityFile.objects.filter(activity=self.activity).exists())

    def test_delete_activity_file(self):
        """Test deleting a file from an activity."""
        self.client.force_authenticate(user=self.teacher)

        # Create a file
        file_instance = ActivityFile.objects.create(
            activity=self.activity,
            filename='Test File',
            file='test.txt'
        )

        url = reverse('activities:delete_file', kwargs={
            'code': 'ACT001',
            'file_id': file_instance.id
        })

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(ActivityFile.objects.filter(id=file_instance.id).exists())

    def test_upload_file_as_non_creator_fails(self):
        """Test that non-creators cannot upload files."""
        another_teacher = User.objects.create_user(
            user_code='teacher_002',
            email='teacher2@example.com',
            password='teacherpass123',
            role=User.Role.TEACHER
        )
        self.client.force_authenticate(user=another_teacher)

        url = reverse('activities:upload_file', kwargs={'code': 'ACT001'})

        test_file = SimpleUploadedFile("test.txt", b"content", content_type="text/plain")
        data = {'file': test_file, 'filename': 'Test'}

        response = self.client.post(url, data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class ActivityStatisticsTests(APITestCase):
    """Tests for activity statistics endpoint."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()

        self.teacher = User.objects.create_user(
            user_code='teacher_001',
            email='teacher@example.com',
            password='teacherpass123',
            role=User.Role.TEACHER
        )

        self.activity = Activity.objects.create(
            code='ACT001',
            title='Test Activity',
            description='<p>Description</p>',
            max_participants_per_meeting=6,
            created_by=self.teacher
        )

    def test_get_activity_statistics(self):
        """Test getting statistics for an activity."""
        self.client.force_authenticate(user=self.teacher)

        url = reverse('activities:activity_statistics', kwargs={'code': 'ACT001'})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['activity_code'], 'ACT001')
        self.assertIn('total_events', response.data)
        self.assertIn('total_enrollments', response.data)
        self.assertIn('attendance_rate', response.data)
