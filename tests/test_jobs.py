"""
Test Suite for Job Application Management (jobs app).
Validates CRUD, filtering, search, sorting, and user data isolation.
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from jobs.models import JobApplication


class JobApplicationCRUDTests(TestCase):
    """
    Tests JobApplication model operations, form validation, views, and data isolation.
    """

    def setUp(self):
        self.client = Client()

        # Create two distinct users to verify data isolation
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='Password123!'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='Password123!'
        )

        # Create job applications for user 1
        self.job1 = JobApplication.objects.create(
            user=self.user1,
            company_name='Google',
            job_title='Python Full Stack Engineer',
            job_location='Hyderabad',
            job_type=JobApplication.JOB_TYPE_FULL_TIME,
            application_status=JobApplication.STATUS_APPLIED,
            application_date=timezone.now().date(),
            salary='₹18 LPA'
        )
        self.job2 = JobApplication.objects.create(
            user=self.user1,
            company_name='Microsoft',
            job_title='Django Backend Developer',
            job_location='Bengaluru',
            job_type=JobApplication.JOB_TYPE_REMOTE,
            application_status=JobApplication.STATUS_SHORTLISTED,
            application_date=timezone.now().date(),
            salary='₹16 LPA'
        )

        # Create job application for user 2
        self.job3 = JobApplication.objects.create(
            user=self.user2,
            company_name='Amazon',
            job_title='Software Development Engineer',
            job_location='Hyderabad',
            job_type=JobApplication.JOB_TYPE_FULL_TIME,
            application_status=JobApplication.STATUS_APPLIED,
            application_date=timezone.now().date()
        )

    def test_job_list_strictly_isolated_to_user(self):
        """User 1 only sees their own applications in job list."""
        self.client.force_login(self.user1)
        response = self.client.get(reverse('job_list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Google')
        self.assertContains(response, 'Microsoft')
        # User 1 MUST NOT see User 2's application
        self.assertNotContains(response, 'Amazon')

    def test_job_detail_user_isolation(self):
        """User 1 cannot view User 2's application (returns 404)."""
        self.client.force_login(self.user1)
        # Attempt to access user2's job
        response = self.client.get(reverse('job_detail', kwargs={'pk': self.job3.pk}))
        self.assertEqual(response.status_code, 404)

        # Access user1's own job
        response = self.client.get(reverse('job_detail', kwargs={'pk': self.job1.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Google')

    def test_job_creation(self):
        """User can create a new job application."""
        self.client.force_login(self.user1)
        payload = {
            'company_name': 'Razorpay',
            'job_title': 'Python Developer',
            'job_location': 'Bengaluru',
            'job_type': JobApplication.JOB_TYPE_FULL_TIME,
            'application_status': JobApplication.STATUS_APPLIED,
            'application_date': '2026-03-15',
            'salary': '₹12 LPA',
            'job_url': 'https://razorpay.com/jobs/123',
            'job_description': 'Looking for an experienced Python developer with Django skills.',
            'notes': 'Referred by alumni.'
        }
        response = self.client.post(reverse('job_create'), data=payload)
        self.assertEqual(response.status_code, 302)

        # Verify record in DB
        created_job = JobApplication.objects.filter(company_name='Razorpay').first()
        self.assertIsNotNone(created_job)
        self.assertEqual(created_job.user, self.user1)
        self.assertEqual(created_job.job_title, 'Python Developer')

    def test_job_update(self):
        """User can update an existing job application."""
        self.client.force_login(self.user1)
        payload = {
            'company_name': 'Google Cloud',
            'job_title': 'Senior Python Engineer',
            'job_location': 'Hyderabad',
            'job_type': JobApplication.JOB_TYPE_FULL_TIME,
            'application_status': JobApplication.STATUS_SHORTLISTED,
            'application_date': str(self.job1.application_date),
            'salary': '₹22 LPA',
        }
        response = self.client.post(
            reverse('job_update', kwargs={'pk': self.job1.pk}),
            data=payload
        )
        self.assertEqual(response.status_code, 302)

        self.job1.refresh_from_db()
        self.assertEqual(self.job1.company_name, 'Google Cloud')
        self.assertEqual(self.job1.application_status, JobApplication.STATUS_SHORTLISTED)

    def test_job_delete(self):
        """User can delete an existing job application."""
        self.client.force_login(self.user1)
        response = self.client.post(
            reverse('job_delete', kwargs={'pk': self.job1.pk})
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(JobApplication.objects.filter(pk=self.job1.pk).exists())

    def test_search_and_filtering(self):
        """Search query filters applications correctly."""
        self.client.force_login(self.user1)

        # Search for 'Microsoft'
        response = self.client.get(reverse('job_list') + '?q=Microsoft')
        self.assertEqual(response.status_code, 200)
        apps = list(response.context['applications'])
        self.assertTrue(any(app.company_name == 'Microsoft' for app in apps))
        self.assertFalse(any(app.company_name == 'Google' for app in apps))

        # Filter by status 'Shortlisted'
        response = self.client.get(reverse('job_list') + '?status=Shortlisted')
        self.assertEqual(response.status_code, 200)
        apps = list(response.context['applications'])
        self.assertTrue(any(app.company_name == 'Microsoft' for app in apps))
        self.assertFalse(any(app.company_name == 'Google' for app in apps))

