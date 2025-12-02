from django.test import TestCase
from django.urls import reverse
from django.utils import timezone as django_timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from datetime import datetime, timedelta
import pytz

from apps.users.models import User
from apps.activities.models import Activity
from .models import Event, Enrollment


class EventModelTests(TestCase):
    """Tests for Event model."""

    def setUp(self):
        """Set up test data."""
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

    def test_create_event(self):
        """Test creating an event."""
        start = django_timezone.now() + timedelta(days=1)
        end = start + timedelta(hours=1)

        event = Event.objects.create(
            activity=self.activity,
            start_datetime=start,
            end_datetime=end,
            waiting_time_minutes=10
        )

        self.assertEqual(event.activity, self.activity)
        self.assertEqual(event.status, Event.Status.SCHEDULED)
        self.assertFalse(event.first_reminder_sent)

    def test_event_enrolled_count(self):
        """Test enrolled count annotation."""
        from django.db.models import Q, Count

        start = django_timezone.now() + timedelta(days=1)
        end = start + timedelta(hours=1)

        event = Event.objects.create(
            activity=self.activity,
            start_datetime=start,
            end_datetime=end
        )

        # Create some enrollments
        student1 = User.objects.create_user(
            user_code='student_001',
            email='student1@test.com',
            password='pass123',
            role=User.Role.STUDENT
        )

        student2 = User.objects.create_user(
            user_code='student_002',
            email='student2@test.com',
            password='pass123',
            role=User.Role.STUDENT
        )

        Enrollment.objects.create(user=student1, event=event, status=Enrollment.Status.ENROLLED)
        Enrollment.objects.create(user=student2, event=event, status=Enrollment.Status.ENROLLED)

        # Test with annotation
        event_with_count = Event.objects.filter(id=event.id).annotate(
            enrolled_count=Count('enrollments', filter=Q(enrollments__status='enrolled'))
        ).first()

        self.assertEqual(event_with_count.enrolled_count, 2)


class EventAPITests(APITestCase):
    """Tests for Event API endpoints."""

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

        # Create activity
        self.activity = Activity.objects.create(
            code='ACT001',
            title='Test Activity',
            description='<p>Description</p>',
            max_participants_per_meeting=6,
            created_by=self.teacher
        )

        # Create events
        self.event1 = Event.objects.create(
            activity=self.activity,
            start_datetime=django_timezone.now() + timedelta(days=1),
            end_datetime=django_timezone.now() + timedelta(days=1, hours=1),
            waiting_time_minutes=10
        )

        self.event2 = Event.objects.create(
            activity=self.activity,
            start_datetime=django_timezone.now() + timedelta(days=2),
            end_datetime=django_timezone.now() + timedelta(days=2, hours=1),
            waiting_time_minutes=10
        )

    def test_list_events(self):
        """Test listing events."""
        self.client.force_authenticate(user=self.student)

        url = reverse('events:event_list_create')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_list_events_filter_by_activity(self):
        """Test filtering events by activity code."""
        self.client.force_authenticate(user=self.student)

        url = reverse('events:event_list_create')
        response = self.client.get(url, {'activity_code': 'ACT001'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_create_event_as_teacher(self):
        """Test creating an event as a teacher."""
        self.client.force_authenticate(user=self.teacher)

        url = reverse('events:event_list_create')
        start = django_timezone.now() + timedelta(days=3)
        end = start + timedelta(hours=1)

        data = {
            'activity_code': 'ACT001',
            'start_datetime': start.isoformat(),
            'end_datetime': end.isoformat(),
            'waiting_time_minutes': 15,
            'first_reminder_minutes': 1440,
            'second_reminder_minutes': 60
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Event.objects.filter(activity=self.activity).count() >= 3)

    def test_create_event_as_student_fails(self):
        """Test that students cannot create events."""
        self.client.force_authenticate(user=self.student)

        url = reverse('events:event_list_create')
        start = django_timezone.now() + timedelta(days=3)
        end = start + timedelta(hours=1)

        data = {
            'activity_code': 'ACT001',
            'start_datetime': start.isoformat(),
            'end_datetime': end.isoformat(),
            'waiting_time_minutes': 10
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_event_in_past_fails(self):
        """Test that creating events in the past fails."""
        self.client.force_authenticate(user=self.teacher)

        url = reverse('events:event_list_create')
        start = django_timezone.now() - timedelta(days=1)
        end = start + timedelta(hours=1)

        data = {
            'activity_code': 'ACT001',
            'start_datetime': start.isoformat(),
            'end_datetime': end.isoformat(),
            'waiting_time_minutes': 10
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('start_datetime', response.data)

    def test_bulk_create_events(self):
        """Test bulk creating events."""
        self.client.force_authenticate(user=self.teacher)

        url = reverse('events:event_bulk_create')

        # Create events for next 3 days at 9:00 and 14:00 UTC
        start_date = (django_timezone.now() + timedelta(days=5)).date()
        end_date = (django_timezone.now() + timedelta(days=7)).date()

        data = {
            'activity_code': 'ACT001',
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'hours_utc': ['09:00', '14:00'],
            'duration_minutes': 60,
            'waiting_time_minutes': 10,
            'first_reminder_minutes': 1440,
            'second_reminder_minutes': 60
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # 3 days * 2 hours = 6 events
        self.assertEqual(len(response.data['events']), 6)

    def test_get_event_detail(self):
        """Test getting event details."""
        self.client.force_authenticate(user=self.student)

        url = reverse('events:event_detail', kwargs={'pk': self.event1.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], str(self.event1.id))

    def test_update_event(self):
        """Test updating an event."""
        self.client.force_authenticate(user=self.teacher)

        url = reverse('events:event_update', kwargs={'pk': self.event1.id})

        data = {
            'waiting_time_minutes': 20,
            'start_datetime': self.event1.start_datetime.isoformat(),
            'end_datetime': self.event1.end_datetime.isoformat()
        }

        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['waiting_time_minutes'], 20)

    def test_delete_event_without_enrollments(self):
        """Test deleting event without enrollments."""
        self.client.force_authenticate(user=self.teacher)

        url = reverse('events:event_delete', kwargs={'pk': self.event1.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Event.objects.filter(id=self.event1.id).exists())

    def test_delete_event_with_enrollments_fails(self):
        """Test that deleting event with enrollments fails."""
        self.client.force_authenticate(user=self.teacher)

        # Create enrollment
        Enrollment.objects.create(
            user=self.student,
            event=self.event1,
            status=Enrollment.Status.ENROLLED
        )

        url = reverse('events:event_delete', kwargs={'pk': self.event1.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(Event.objects.filter(id=self.event1.id).exists())


class EnrollmentAPITests(APITestCase):
    """Tests for Enrollment API endpoints."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()

        self.student = User.objects.create_user(
            user_code='student_001',
            email='student@example.com',
            password='studentpass123',
            role=User.Role.STUDENT
        )

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

        self.event = Event.objects.create(
            activity=self.activity,
            start_datetime=django_timezone.now() + timedelta(days=1),
            end_datetime=django_timezone.now() + timedelta(days=1, hours=1),
            waiting_time_minutes=10
        )

    def test_enroll_in_event(self):
        """Test enrolling in an event."""
        self.client.force_authenticate(user=self.student)

        url = reverse('events:enroll_event')
        data = {'event_id': str(self.event.id)}

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Enrollment.objects.filter(user=self.student, event=self.event).exists()
        )

    def test_enroll_twice_fails(self):
        """Test that enrolling twice in same event fails."""
        self.client.force_authenticate(user=self.student)

        # First enrollment
        Enrollment.objects.create(
            user=self.student,
            event=self.event,
            status=Enrollment.Status.ENROLLED
        )

        # Try to enroll again
        url = reverse('events:enroll_event')
        data = {'event_id': str(self.event.id)}

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unenroll_from_event(self):
        """Test unenrolling from an event."""
        self.client.force_authenticate(user=self.student)

        # First enroll
        enrollment = Enrollment.objects.create(
            user=self.student,
            event=self.event,
            status=Enrollment.Status.ENROLLED
        )

        # Unenroll
        url = reverse('events:unenroll_event', kwargs={'event_id': self.event.id})
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check enrollment is cancelled
        enrollment.refresh_from_db()
        self.assertEqual(enrollment.status, Enrollment.Status.CANCELLED)

    def test_my_enrollments(self):
        """Test getting my enrollments."""
        self.client.force_authenticate(user=self.student)

        # Create enrollments
        Enrollment.objects.create(
            user=self.student,
            event=self.event,
            status=Enrollment.Status.ENROLLED
        )

        url = reverse('events:my_enrollments')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_view_event_enrollments_as_teacher(self):
        """Test viewing event enrollments as teacher."""
        self.client.force_authenticate(user=self.teacher)

        # Create enrollments
        Enrollment.objects.create(
            user=self.student,
            event=self.event,
            status=Enrollment.Status.ENROLLED
        )

        url = reverse('events:event_enrollments', kwargs={'pk': self.event.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_view_event_enrollments_as_student_fails(self):
        """Test that students cannot view event enrollments."""
        self.client.force_authenticate(user=self.student)

        url = reverse('events:event_enrollments', kwargs={'pk': self.event.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TimezoneConversionTests(APITestCase):
    """Tests for timezone conversion."""

    def setUp(self):
        """Set up test client."""
        self.client = APIClient()

        self.student = User.objects.create_user(
            user_code='student_001',
            email='student@example.com',
            password='studentpass123',
            role=User.Role.STUDENT
        )

    def test_convert_timezone(self):
        """Test converting timezone."""
        self.client.force_authenticate(user=self.student)

        url = reverse('events:convert_timezone')

        # Convert UTC to Mexico City time
        utc_time = datetime(2024, 1, 15, 14, 0, 0, tzinfo=pytz.UTC)

        data = {
            'datetime_utc': utc_time.isoformat(),
            'target_timezone': 'America/Mexico_City'
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('datetime_local', response.data)
        self.assertEqual(response.data['timezone'], 'America/Mexico_City')

    def test_convert_invalid_timezone_fails(self):
        """Test that invalid timezone fails."""
        self.client.force_authenticate(user=self.student)

        url = reverse('events:convert_timezone')

        data = {
            'datetime_utc': datetime.now(pytz.UTC).isoformat(),
            'target_timezone': 'Invalid/Timezone'
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class EventStatisticsTests(APITestCase):
    """Tests for event statistics."""

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

        self.event = Event.objects.create(
            activity=self.activity,
            start_datetime=django_timezone.now() + timedelta(days=1),
            end_datetime=django_timezone.now() + timedelta(days=1, hours=1),
            waiting_time_minutes=10
        )

    def test_get_event_statistics(self):
        """Test getting event statistics."""
        self.client.force_authenticate(user=self.teacher)

        # Create some enrollments
        student1 = User.objects.create_user(
            user_code='student_001',
            email='student1@test.com',
            password='pass123',
            role=User.Role.STUDENT
        )

        student2 = User.objects.create_user(
            user_code='student_002',
            email='student2@test.com',
            password='pass123',
            role=User.Role.STUDENT
        )

        Enrollment.objects.create(user=student1, event=self.event, status=Enrollment.Status.ENROLLED)
        Enrollment.objects.create(user=student2, event=self.event, status=Enrollment.Status.ENROLLED)

        url = reverse('events:event_statistics', kwargs={'pk': self.event.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_enrolled'], 2)
        self.assertEqual(response.data['activity_code'], 'ACT001')
