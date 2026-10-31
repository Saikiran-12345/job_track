"""
Django REST Framework Serializers for JobTrack API.

Provides JSON serialization, deserialization, and input validation for
JobApplication, Interview, User, and Dashboard statistics.
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from jobs.models import JobApplication
from interviews.models import Interview


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for authenticated user profile."""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['id', 'username', 'date_joined']


class InterviewMiniSerializer(serializers.ModelSerializer):
    """Compact interview representation nested inside JobApplication."""
    class Meta:
        model = Interview
        fields = [
            'id',
            'interview_round',
            'interview_date',
            'status',
            'location_or_link',
            'notes_or_feedback',
        ]


class JobApplicationSerializer(serializers.ModelSerializer):
    """
    Serializer for JobApplication entity.
    Includes read-only user handle, related interviews list, and badge class.
    """
    user = serializers.ReadOnlyField(source='user.username')
    status_badge = serializers.ReadOnlyField(source='get_status_badge_class')
    interviews = InterviewMiniSerializer(many=True, read_only=True)

    class Meta:
        model = JobApplication
        fields = [
            'id',
            'user',
            'company_name',
            'job_title',
            'job_description',
            'job_location',
            'job_type',
            'salary',
            'application_date',
            'application_status',
            'job_url',
            'notes',
            'status_badge',
            'interviews',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def validate_company_name(self, value):
        """Sanitize and ensure company name is not purely whitespace."""
        val = value.strip()
        if not val:
            raise serializers.ValidationError("Company name cannot be blank.")
        return val

    def validate_job_title(self, value):
        """Sanitize and ensure job title is not purely whitespace."""
        val = value.strip()
        if not val:
            raise serializers.ValidationError("Job title cannot be blank.")
        return val


class InterviewSerializer(serializers.ModelSerializer):
    """
    Serializer for Interview entity.
    Validates that the linked job_application belongs strictly to the requesting user.
    """
    company_name = serializers.ReadOnlyField(source='job_application.company_name')
    job_title = serializers.ReadOnlyField(source='job_application.job_title')

    class Meta:
        model = Interview
        fields = [
            'id',
            'job_application',
            'company_name',
            'job_title',
            'interview_round',
            'interview_date',
            'status',
            'location_or_link',
            'notes_or_feedback',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'company_name', 'job_title', 'created_at', 'updated_at']

    def validate_job_application(self, value):
        """
        Security validation: Ensure the job_application belongs to the requesting user.
        Prevents a user from attaching interviews to another user's job application.
        """
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            if value.user != request.user:
                raise serializers.ValidationError(
                    "You do not have permission to attach an interview to this job application."
                )
        return value
