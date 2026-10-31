"""
Test Suite for Interview Management (interviews app).
Validates interview scheduling, round types, status lifecycle progression, and user data isolation.
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from jobs.models import JobApplication
from interviews.models import Interview


class InterviewManagementTests(TestCase):
    """
    Tests Interview CRUD, security isolation, and status updates.
    """

    def setUp(self):
        self.client = Client()

        # Two users for testing isolation
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

        # Job application for user 1
        self.job1 = JobApplication.objects.create(
            user=self.user1,
            company_name='Flipkart',
            job_title='Software Engineer',
            job_location='Bengaluru',
            job_type=JobApplication.JOB_TYPE_FULL_TIME,
            application_status=JobApplication.STATUS_APPLIED,
            application_date=timezone.now().date()
        )

        # Job application for user 2
        self.job2 = JobApplication.objects.create(
            user=self.user2,
            company_name='Swiggy',
            job_title='Backend Developer',
            job_location='Bengaluru',
            job_type=JobApplication.JOB_TYPE_FULL_TIME,
            application_status=JobApplication.STATUS_APPLIED,
            application_date=timezone.now().date()
        )

        # Existing interview for user 1
        self.interview1 = Interview.objects.create(
            job_application=self.job1,
            interview_round=Interview.ROUND_TECHNICAL,
            interview_date=timezone.now() + timedelta(days=2),
            status=Interview.STATUS_SCHEDULED,
            location_or_link='https://meet.google.com/abc-defg-hij',
            notes_or_feedback='Focus on Python OOP and SQL queries.'
        )

    def test_interview_list_isolation(self):
        """User 1 only sees interviews for their own applications."""
        self.client.force_login(self.user1)
        response = self.client.get(reverse('interview_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Flipkart')
        self.assertNotContains(response, 'Swiggy')

    def test_schedule_interview_and_auto_status_progression(self):
        """Scheduling an interview automatically moves an 'Applied' job to 'Interview' status."""
        self.client.force_login(self.user1)

        interview_time = (timezone.now() + timedelta(days=5)).strftime('%Y-%m-%dT%H:%M')
        payload = {
            'job_application': self.job1.pk,
            'interview_round': Interview.ROUND_HR,
            'interview_date': interview_time,
            'status': Interview.STATUS_SCHEDULED,
            'location_or_link': 'https://zoom.us/j/123456789',
            'notes_or_feedback': 'HR behavioral round.'
        }
        response = self.client.post(reverse('interview_create'), data=payload)
        self.assertEqual(response.status_code, 302)

        # Verify new interview was created
        new_interview = Interview.objects.filter(
            job_application=self.job1,
            interview_round=Interview.ROUND_HR
        ).first()
        self.assertIsNotNone(new_interview)

        # Verify job application status was progressed from 'Applied' to 'Interview'
        self.job1.refresh_from_db()
        self.assertEqual(self.job1.application_status, JobApplication.STATUS_INTERVIEW)

    def test_user_cannot_schedule_interview_for_another_users_job(self):
        """User 1 cannot schedule an interview using User 2's job application."""
        self.client.force_login(self.user1)

        interview_time = (timezone.now() + timedelta(days=3)).strftime('%Y-%m-%dT%H:%M')
        payload = {
            'job_application': self.job2.pk,  # Belongs to user 2!
            'interview_round': Interview.ROUND_TECHNICAL,
            'interview_date': interview_time,
            'status': Interview.STATUS_SCHEDULED,
        }
        response = self.client.post(reverse('interview_create'), data=payload)
        # Form validation should fail because self.job2 is not in user1's queryset
        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response,
            'form',
            'job_application',
            'Select a valid choice. That choice is not one of the available choices.'
        )

    def test_interview_update(self):
        """User can update interview status and notes."""
        self.client.force_login(self.user1)
        interview_time = self.interview1.interview_date.strftime('%Y-%m-%dT%H:%M')
        payload = {
            'job_application': self.job1.pk,
            'interview_round': Interview.ROUND_TECHNICAL,
            'interview_date': interview_time,
            'status': Interview.STATUS_COMPLETED,
            'location_or_link': self.interview1.location_or_link,
            'notes_or_feedback': 'Cleared round! System design questions answered well.'
        }
        response = self.client.post(
            reverse('interview_update', kwargs={'pk': self.interview1.pk}),
            data=payload
        )
        self.assertEqual(response.status_code, 302)

        self.interview1.refresh_from_db()
        self.assertEqual(self.interview1.status, Interview.STATUS_COMPLETED)
        self.assertIn('Cleared round', self.interview1.notes_or_feedback)

    def test_interview_delete(self):
        """User can delete an interview record."""
        self.client.force_login(self.user1)
        response = self.client.post(
            reverse('interview_delete', kwargs={'pk': self.interview1.pk})
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Interview.objects.filter(pk=self.interview1.pk).exists())
