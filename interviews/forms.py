"""
Interviews Forms for JobTrack.

Provides InterviewForm with user-restricted JobApplication queryset,
HTML5 datetime-local widget, and Bootstrap 5 styles.
"""

from django import forms
from .models import Interview
from jobs.models import JobApplication


class InterviewForm(forms.ModelForm):
    """
    Form for scheduling and updating interviews.
    Ensures that users can only schedule interviews for their own job applications.
    """
    class Meta:
        model = Interview
        fields = [
            'job_application',
            'interview_round',
            'interview_date',
            'status',
            'location_or_link',
            'notes_or_feedback',
        ]
        widgets = {
            'job_application': forms.Select(attrs={
                'class': 'form-select',
                'required': True,
            }),
            'interview_round': forms.Select(attrs={
                'class': 'form-select',
            }),
            'interview_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
            }),
            'status': forms.Select(attrs={
                'class': 'form-select',
            }),
            'location_or_link': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Google Meet link, Zoom URL, or Office Address',
            }),
            'notes_or_feedback': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Topics to prepare, questions asked, technical feedback...',
            }),
        }

    def __init__(self, *args, user=None, initial_job=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user is not None:
            # Strictly limit job applications to those owned by the current user
            self.fields['job_application'].queryset = JobApplication.objects.filter(user=user)
        
        if initial_job is not None:
            self.fields['job_application'].initial = initial_job
