"""
Dashboard and Analytics Views for JobTrack.

Computes live database metrics, application status breakdowns,
upcoming interviews, and monthly application trends.
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import JobApplication


@login_required
def dashboard_view(request):
    """
    Renders the central user dashboard showing summary metrics,
    recent applications, and upcoming interviews.
    """
    user_apps = JobApplication.objects.filter(user=request.user)

    # Database-driven statistics
    total_count = user_apps.count()
    applied_count = user_apps.filter(application_status=JobApplication.STATUS_APPLIED).count()
    shortlisted_count = user_apps.filter(application_status=JobApplication.STATUS_SHORTLISTED).count()
    interview_count = user_apps.filter(application_status=JobApplication.STATUS_INTERVIEW).count()
    selected_count = user_apps.filter(application_status=JobApplication.STATUS_SELECTED).count()
    rejected_count = user_apps.filter(application_status=JobApplication.STATUS_REJECTED).count()

    # Recent 5 applications
    recent_applications = user_apps.order_by('-created_at')[:5]

    # Upcoming interviews (interviews app)
    upcoming_interviews = []
    try:
        from interviews.models import Interview
        upcoming_interviews = Interview.objects.filter(
            job_application__user=request.user,
            interview_date__gte=timezone.now(),
            status='Scheduled'
        ).select_related('job_application').order_by('interview_date')[:5]
    except Exception:
        upcoming_interviews = []

    context = {
        'title': 'Dashboard',
        'total_count': total_count,
        'applied_count': applied_count,
        'shortlisted_count': shortlisted_count,
        'interview_count': interview_count,
        'selected_count': selected_count,
        'rejected_count': rejected_count,
        'recent_applications': recent_applications,
        'upcoming_interviews': upcoming_interviews,
    }
    return render(request, 'jobs/dashboard.html', context)


@login_required
def analytics_view(request):
    """
    Renders detailed analytics with status distribution and monthly trends.
    """
    user_apps = JobApplication.objects.filter(user=request.user)

    total_count = user_apps.count()
    status_counts = {
        'Applied': user_apps.filter(application_status=JobApplication.STATUS_APPLIED).count(),
        'Shortlisted': user_apps.filter(application_status=JobApplication.STATUS_SHORTLISTED).count(),
        'Interview': user_apps.filter(application_status=JobApplication.STATUS_INTERVIEW).count(),
        'Selected': user_apps.filter(application_status=JobApplication.STATUS_SELECTED).count(),
        'Rejected': user_apps.filter(application_status=JobApplication.STATUS_REJECTED).count(),
    }

    job_type_counts = {
        'Full Time': user_apps.filter(job_type=JobApplication.JOB_TYPE_FULL_TIME).count(),
        'Part Time': user_apps.filter(job_type=JobApplication.JOB_TYPE_PART_TIME).count(),
        'Internship': user_apps.filter(job_type=JobApplication.JOB_TYPE_INTERNSHIP).count(),
        'Remote': user_apps.filter(job_type=JobApplication.JOB_TYPE_REMOTE).count(),
        'Contract': user_apps.filter(job_type=JobApplication.JOB_TYPE_CONTRACT).count(),
    }

    context = {
        'title': 'Analytics & Reports',
        'total_count': total_count,
        'status_counts': status_counts,
        'job_type_counts': job_type_counts,
    }
    return render(request, 'jobs/analytics.html', context)
