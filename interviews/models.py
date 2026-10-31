"""
JobTrack Interviews App Models.

Defines the Interview model associated with JobApplication,
including interview rounds, date/time, status, and feedback notes.
"""

from django.db import models
from django.utils import timezone
from jobs.models import JobApplication


class Interview(models.Model):
    """
    Represents an interview scheduled for a particular JobApplication.
    Each interview is linked to a JobApplication, which in turn belongs to a User.
    """

    # Interview Round Choices
    ROUND_TECHNICAL = 'Technical'
    ROUND_HR = 'HR'
    ROUND_ONLINE = 'Online'
    ROUND_IN_PERSON = 'In-person'

    ROUND_CHOICES = [
        (ROUND_TECHNICAL, 'Technical'),
        (ROUND_HR, 'HR'),
        (ROUND_ONLINE, 'Online'),
        (ROUND_IN_PERSON, 'In-person'),
    ]

    # Status Choices
    STATUS_SCHEDULED = 'Scheduled'
    STATUS_COMPLETED = 'Completed'
    STATUS_CANCELLED = 'Cancelled'

    STATUS_CHOICES = [
        (STATUS_SCHEDULED, 'Scheduled'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    job_application = models.ForeignKey(
        JobApplication,
        on_delete=models.CASCADE,
        related_name='interviews',
        help_text="The job application this interview is for."
    )
    interview_round = models.CharField(
        max_length=30,
        choices=ROUND_CHOICES,
        default=ROUND_TECHNICAL,
        help_text="Type/round of interview (Technical, HR, Online, In-person)."
    )
    interview_date = models.DateTimeField(
        default=timezone.now,
        help_text="Scheduled date and time of the interview."
    )
    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default=STATUS_SCHEDULED,
        help_text="Status of the interview."
    )
    location_or_link = models.CharField(
        max_length=255,
        blank=True,
        help_text="Meeting link (Google Meet, Zoom, Teams) or office location address."
    )
    notes_or_feedback = models.TextField(
        blank=True,
        help_text="Questions asked, key topics covered, or interviewer feedback."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-interview_date']
        indexes = [
            models.Index(fields=['job_application', 'interview_date']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.interview_round} interview for {self.job_application.job_title} at {self.job_application.company_name}"

    @property
    def is_upcoming(self):
        """Returns True if the interview date is in the future and marked Scheduled."""
        return self.interview_date >= timezone.now() and self.status == self.STATUS_SCHEDULED
