"""
JobTrack Jobs App Models.

Defines the JobApplication entity with choice tuples, timestamps,
user isolation via foreign key, and utility methods.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class JobApplication(models.Model):
    """
    Represents an individual job application submitted by a user.
    Each record belongs strictly to one authenticated User.
    """

    # Application Status Choices
    STATUS_APPLIED = 'Applied'
    STATUS_SHORTLISTED = 'Shortlisted'
    STATUS_INTERVIEW = 'Interview'
    STATUS_SELECTED = 'Selected'
    STATUS_REJECTED = 'Rejected'

    STATUS_CHOICES = [
        (STATUS_APPLIED, 'Applied'),
        (STATUS_SHORTLISTED, 'Shortlisted'),
        (STATUS_INTERVIEW, 'Interview'),
        (STATUS_SELECTED, 'Selected'),
        (STATUS_REJECTED, 'Rejected'),
    ]

    # Job Type Choices
    JOB_TYPE_FULL_TIME = 'Full Time'
    JOB_TYPE_PART_TIME = 'Part Time'
    JOB_TYPE_INTERNSHIP = 'Internship'
    JOB_TYPE_REMOTE = 'Remote'
    JOB_TYPE_CONTRACT = 'Contract'

    JOB_TYPE_CHOICES = [
        (JOB_TYPE_FULL_TIME, 'Full Time'),
        (JOB_TYPE_PART_TIME, 'Part Time'),
        (JOB_TYPE_INTERNSHIP, 'Internship'),
        (JOB_TYPE_REMOTE, 'Remote'),
        (JOB_TYPE_CONTRACT, 'Contract'),
    ]

    # Database Fields
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='job_applications',
        help_text="The user who created and owns this job application."
    )
    company_name = models.CharField(
        max_length=150,
        help_text="Name of the company (e.g. Google, Infosys, TCS, Startup)."
    )
    job_title = models.CharField(
        max_length=150,
        help_text="Designation or position applied for (e.g. Python Developer, Django Engineer)."
    )
    job_description = models.TextField(
        blank=True,
        help_text="Key responsibilities or pasted job description requirements."
    )
    job_location = models.CharField(
        max_length=100,
        help_text="City or location (e.g. Hyderabad, Bengaluru, Remote, Pune)."
    )
    job_type = models.CharField(
        max_length=30,
        choices=JOB_TYPE_CHOICES,
        default=JOB_TYPE_FULL_TIME,
        help_text="Employment type."
    )
    salary = models.CharField(
        max_length=50,
        blank=True,
        help_text="Offered/expected salary or CTC (e.g. ₹6 LPA, $80,000/yr)."
    )
    application_date = models.DateField(
        default=timezone.now,
        help_text="Date when you submitted the application."
    )
    application_status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default=STATUS_APPLIED,
        help_text="Current progress stage of the application."
    )
    job_url = models.URLField(
        blank=True,
        help_text="Direct link to the job posting (LinkedIn, Naukri, Company site)."
    )
    notes = models.TextField(
        blank=True,
        help_text="Personal notes, referral contact, or preparation strategy."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-application_date', '-created_at']
        indexes = [
            models.Index(fields=['user', 'application_status']),
            models.Index(fields=['user', 'company_name']),
        ]

    def __str__(self):
        return f"{self.job_title} at {self.company_name} ({self.application_status})"

    def get_status_badge_class(self):
        """
        Returns the appropriate CSS class for Bootstrap styling based on status.
        """
        badge_map = {
            self.STATUS_APPLIED: 'badge-status-applied',
            self.STATUS_SHORTLISTED: 'badge-status-shortlisted',
            self.STATUS_INTERVIEW: 'badge-status-interview',
            self.STATUS_SELECTED: 'badge-status-selected',
            self.STATUS_REJECTED: 'badge-status-rejected',
        }
        return badge_map.get(self.application_status, 'bg-secondary')
