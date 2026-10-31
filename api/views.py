"""
Django REST Framework API Views for JobTrack.

Implements ViewSets for JobApplication and Interview with strict user isolation,
search/filtering, lifecycle progression, and custom summary analytics endpoints.
"""

from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q
from django.utils import timezone

from jobs.models import JobApplication
from interviews.models import Interview
from .serializers import (
    JobApplicationSerializer,
    InterviewSerializer,
    UserProfileSerializer,
)


class JobApplicationViewSet(viewsets.ModelViewSet):
    """
    CRUD API endpoint for Job Applications.
    
    Actions:
    - GET /api/applications/ : List all job applications for the authenticated user.
    - POST /api/applications/ : Create a new job application.
    - GET /api/applications/{id}/ : Retrieve a specific application.
    - PUT/PATCH /api/applications/{id}/ : Update an application.
    - DELETE /api/applications/{id}/ : Delete an application.
    """
    serializer_class = JobApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Enforce user data isolation: Only return applications created by the requesting user.
        Supports search and filtering via query parameters.
        """
        queryset = JobApplication.objects.filter(user=self.request.user).prefetch_related('interviews')

        # Filter by search keyword (company or title)
        search = self.request.query_params.get('search', '').strip()
        if search:
            queryset = queryset.filter(
                Q(company_name__icontains=search) |
                Q(job_title__icontains=search) |
                Q(job_location__icontains=search)
            )

        # Filter by status
        app_status = self.request.query_params.get('status', '').strip()
        if app_status:
            queryset = queryset.filter(application_status=app_status)

        # Filter by job type
        job_type = self.request.query_params.get('job_type', '').strip()
        if job_type:
            queryset = queryset.filter(job_type=job_type)

        return queryset

    def perform_create(self, serializer):
        """Automatically associate the new application with the authenticated user."""
        serializer.save(user=self.request.user)


class InterviewViewSet(viewsets.ModelViewSet):
    """
    CRUD API endpoint for Scheduled Interviews.
    
    Actions:
    - GET /api/interviews/ : List all interviews for the authenticated user.
    - POST /api/interviews/ : Schedule a new interview.
    - GET /api/interviews/{id}/ : Retrieve interview details.
    - PUT/PATCH /api/interviews/{id}/ : Update interview details or feedback.
    - DELETE /api/interviews/{id}/ : Cancel/delete an interview.
    """
    serializer_class = InterviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Enforce user data isolation: Only return interviews belonging to the user's applications.
        Supports filtering by status (e.g. Scheduled, Completed).
        """
        queryset = Interview.objects.filter(
            job_application__user=self.request.user
        ).select_related('job_application')

        round_status = self.request.query_params.get('status', '').strip()
        if round_status:
            queryset = queryset.filter(status=round_status)

        return queryset

    def perform_create(self, serializer):
        """
        Save the interview and automatically advance the application status
        from 'Applied' to 'Interview' if appropriate.
        """
        interview = serializer.save()
        if interview.job_application.application_status == JobApplication.STATUS_APPLIED:
            interview.job_application.application_status = JobApplication.STATUS_INTERVIEW
            interview.job_application.save(update_fields=['application_status'])


class DashboardStatsAPIView(APIView):
    """
    API endpoint returning live aggregated metrics and conversion rates.
    GET /api/dashboard/
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user_apps = JobApplication.objects.filter(user=request.user)
        total_count = user_apps.count()

        applied = user_apps.filter(application_status=JobApplication.STATUS_APPLIED).count()
        shortlisted = user_apps.filter(application_status=JobApplication.STATUS_SHORTLISTED).count()
        interview = user_apps.filter(application_status=JobApplication.STATUS_INTERVIEW).count()
        selected = user_apps.filter(application_status=JobApplication.STATUS_SELECTED).count()
        rejected = user_apps.filter(application_status=JobApplication.STATUS_REJECTED).count()

        interview_rate = round(((interview + selected) / total_count) * 100, 1) if total_count > 0 else 0
        selection_rate = round((selected / total_count) * 100, 1) if total_count > 0 else 0

        upcoming_interviews_count = Interview.objects.filter(
            job_application__user=request.user,
            interview_date__gte=timezone.now(),
            status='Scheduled'
        ).count()

        data = {
            'total_applications': total_count,
            'status_breakdown': {
                'applied': applied,
                'shortlisted': shortlisted,
                'interview': interview,
                'selected': selected,
                'rejected': rejected,
            },
            'rates': {
                'interview_rate_percentage': interview_rate,
                'selection_rate_percentage': selection_rate,
            },
            'upcoming_interviews_count': upcoming_interviews_count,
        }
        return Response(data, status=status.HTTP_200_OK)


class CurrentUserProfileAPIView(APIView):
    """
    API endpoint returning authenticated user's profile details.
    GET /api/user/
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
