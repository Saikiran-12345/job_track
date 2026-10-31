"""
Test Suite for JobTrack REST API endpoints (api app).
Tests authentication, permissions, CRUD on applications and interviews,
user data isolation, and dashboard analytics API.
"""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIClient
from rest_framework import status

from jobs.models import JobApplication
from interviews.models import Interview


class JobTrackAPITests(TestCase):
    """
    Validates DRF API endpoints, authentication, isolation, and CRUD operations.
    """

    def setUp(self):
        self.client = APIClient()

        # Create two distinct test users
        self.user1 = User.objects.create_user(
            username='apiuser1',
            email='apiuser1@example.com',
            password='Password123!'
        )
        self.user2 = User.objects.create_user(
            username='apiuser2',
            email='apiuser2@example.com',
            password='Password123!'
        )

        # Create Job Application for user 1
        self.job1 = JobApplication.objects.create(
            user=self.user1,
            company_name='Oracle',
            job_title='Python Software Engineer',
            job_location='Hyderabad',
            job_type=JobApplication.JOB_TYPE_FULL_TIME,
            application_status=JobApplication.STATUS_APPLIED,
            application_date=timezone.now().date(),
            salary='₹14 LPA'
        )

        # Create Job Application for user 2
        self.job2 = JobApplication.objects.create(
            user=self.user2,
            company_name='Cisco',
            job_title='Network Automation Engineer',
            job_location='Bengaluru',
            job_type=JobApplication.JOB_TYPE_REMOTE,
            application_status=JobApplication.STATUS_APPLIED,
            application_date=timezone.now().date()
        )

        # Create interview for user 1
        self.interview1 = Interview.objects.create(
            job_application=self.job1,
            interview_round=Interview.ROUND_TECHNICAL,
            interview_date=timezone.now() + timedelta(days=3),
            status=Interview.STATUS_SCHEDULED,
            location_or_link='https://meet.google.com/xyz-api-test'
        )

    def test_unauthenticated_request_denied(self):
        """Unauthenticated requests must be denied with 403 Forbidden."""
        response = self.client.get('/api/applications/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_api_list_applications_user_isolation(self):
        """Authenticated user only sees their own applications in API response."""
        self.client.force_authenticate(user=self.user1)
        response = self.client.get('/api/applications/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data.get('results', response.data)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['company_name'], 'Oracle')

        # Verify user 2's application is not included
        company_names = [item['company_name'] for item in results]
        self.assertNotIn('Cisco', company_names)

    def test_api_create_application(self):
        """Authenticated user can create a new application via REST API."""
        self.client.force_authenticate(user=self.user1)
        payload = {
            'company_name': 'Atlassian',
            'job_title': 'Django Backend Engineer',
            'job_location': 'Bengaluru',
            'job_type': 'Full Time',
            'application_status': 'Applied',
            'application_date': '2026-04-01',
            'salary': '₹20 LPA',
            'job_description': 'Working with Django, PostgreSQL/MySQL, and REST APIs.',
            'notes': 'Applied through company careers portal.'
        }
        response = self.client.post('/api/applications/', data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check in database
        app = JobApplication.objects.filter(company_name='Atlassian').first()
        self.assertIsNotNone(app)
        self.assertEqual(app.user, self.user1)
        self.assertEqual(app.job_title, 'Django Backend Engineer')

    def test_api_retrieve_application_isolation(self):
        """User cannot retrieve another user's application via API (returns 404)."""
        self.client.force_authenticate(user=self.user1)

        # Attempt to retrieve User 2's application
        response = self.client.get(f'/api/applications/{self.job2.pk}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Retrieve user 1's own application
        response = self.client.get(f'/api/applications/{self.job1.pk}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['company_name'], 'Oracle')

    def test_api_update_application(self):
        """Authenticated user can update their job application via PATCH."""
        self.client.force_authenticate(user=self.user1)
        payload = {
            'application_status': 'Shortlisted',
            'salary': '₹16 LPA'
        }
        response = self.client.patch(f'/api/applications/{self.job1.pk}/', data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.job1.refresh_from_db()
        self.assertEqual(self.job1.application_status, 'Shortlisted')
        self.assertEqual(self.job1.salary, '₹16 LPA')

    def test_api_delete_application(self):
        """Authenticated user can delete their application via DELETE."""
        self.client.force_authenticate(user=self.user1)
        response = self.client.delete(f'/api/applications/{self.job1.pk}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(JobApplication.objects.filter(pk=self.job1.pk).exists())

    def test_api_schedule_interview_and_auto_status(self):
        """Scheduling an interview via API succeeds and automatically updates job status."""
        self.client.force_authenticate(user=self.user1)
        interview_time = (timezone.now() + timedelta(days=4)).isoformat()
        payload = {
            'job_application': self.job1.pk,
            'interview_round': 'HR',
            'interview_date': interview_time,
            'status': 'Scheduled',
            'location_or_link': 'https://zoom.us/j/987654321',
            'notes_or_feedback': 'HR discussion about compensation and culture.'
        }
        response = self.client.post('/api/interviews/', data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.job1.refresh_from_db()
        self.assertEqual(self.job1.application_status, JobApplication.STATUS_INTERVIEW)

    def test_api_prevent_scheduling_for_other_users_job(self):
        """User 1 cannot schedule an interview for User 2's application."""
        self.client.force_authenticate(user=self.user1)
        interview_time = (timezone.now() + timedelta(days=2)).isoformat()
        payload = {
            'job_application': self.job2.pk,  # Belongs to user 2
            'interview_round': 'Technical',
            'interview_date': interview_time,
            'status': 'Scheduled'
        }
        response = self.client.post('/api/interviews/', data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_api_dashboard_endpoint(self):
        """GET /api/dashboard/ returns live counts and conversion statistics."""
        self.client.force_authenticate(user=self.user1)
        response = self.client.get('/api/dashboard/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data['total_applications'], 1)
        self.assertIn('status_breakdown', response.data)
        self.assertIn('rates', response.data)
        self.assertEqual(response.data['status_breakdown']['applied'], 1)

    def test_api_user_profile_endpoint(self):
        """GET /api/user/ returns authenticated user profile info."""
        self.client.force_authenticate(user=self.user1)
        response = self.client.get('/api/user/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'apiuser1')
        self.assertEqual(response.data['email'], 'apiuser1@example.com')
