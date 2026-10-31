"""
Jobs Forms for JobTrack.

Provides JobApplicationForm with Bootstrap 5 widgets and HTML5 date picker.
"""

from django import forms
from .models import JobApplication


class JobApplicationForm(forms.ModelForm):
    """
    Form for creating and editing job applications.
    Applies Bootstrap 5 classes to all form inputs.
    """
    class Meta:
        model = JobApplication
        fields = [
            'company_name',
            'job_title',
            'job_location',
            'job_type',
            'application_status',
            'salary',
            'application_date',
            'job_url',
            'job_description',
            'notes',
        ]
        widgets = {
            'company_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Google, Infosys, Tech Mahindra',
                'required': True,
            }),
            'job_title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Python Full Stack Developer, Django Engineer',
                'required': True,
            }),
            'job_location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Hyderabad, Bengaluru, Remote',
                'required': True,
            }),
            'job_type': forms.Select(attrs={
                'class': 'form-select',
            }),
            'application_status': forms.Select(attrs={
                'class': 'form-select',
            }),
            'salary': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. ₹6,50,000 / year or Negotiable',
            }),
            'application_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'job_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://linkedin.com/jobs/view/...',
            }),
            'job_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Paste job summary, key skill requirements, or role overview...',
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Personal notes (e.g., referred by John, follow up on Tuesday)...',
            }),
        }

    def clean_company_name(self):
        """Sanitize and strip whitespace from company name."""
        company = self.cleaned_data.get('company_name', '').strip()
        if not company:
            raise forms.ValidationError("Company name is required.")
        return company

    def clean_job_title(self):
        """Sanitize and strip whitespace from job title."""
        title = self.cleaned_data.get('job_title', '').strip()
        if not title:
            raise forms.ValidationError("Job title is required.")
        return title
