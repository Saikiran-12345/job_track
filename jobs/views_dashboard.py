"""
Dashboard and Analytics Views for JobTrack.

Computes live database metrics, application status breakdowns,
upcoming interviews, conversion rates, and monthly application trends for Chart.js.
"""

import json
from datetime import datetime
from collections import OrderedDict
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

    # Success & conversion metrics
    interview_rate = round(((interview_count + selected_count) / total_count) * 100, 1) if total_count > 0 else 0
    selection_rate = round((selected_count / total_count) * 100, 1) if total_count > 0 else 0

    # Recent 5 applications
    recent_applications = user_apps.order_by('-created_at')[:5]

    # Upcoming interviews
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
        'interview_rate': interview_rate,
        'selection_rate': selection_rate,
        'recent_applications': recent_applications,
        'upcoming_interviews': upcoming_interviews,
    }
    return render(request, 'jobs/dashboard.html', context)


@login_required
def analytics_view(request):
    """
    Renders detailed analytics with status distribution, job type breakdown,
    and monthly application trend charts powered by Chart.js.
    """
    user_apps = JobApplication.objects.filter(user=request.user)
    total_count = user_apps.count()

    # 1. Status Distribution
    status_counts = OrderedDict([
        ('Applied', user_apps.filter(application_status=JobApplication.STATUS_APPLIED).count()),
        ('Shortlisted', user_apps.filter(application_status=JobApplication.STATUS_SHORTLISTED).count()),
        ('Interview', user_apps.filter(application_status=JobApplication.STATUS_INTERVIEW).count()),
        ('Selected', user_apps.filter(application_status=JobApplication.STATUS_SELECTED).count()),
        ('Rejected', user_apps.filter(application_status=JobApplication.STATUS_REJECTED).count()),
    ])

    # 2. Job Type Breakdown
    job_type_counts = OrderedDict([
        ('Full Time', user_apps.filter(job_type=JobApplication.JOB_TYPE_FULL_TIME).count()),
        ('Part Time', user_apps.filter(job_type=JobApplication.JOB_TYPE_PART_TIME).count()),
        ('Internship', user_apps.filter(job_type=JobApplication.JOB_TYPE_INTERNSHIP).count()),
        ('Remote', user_apps.filter(job_type=JobApplication.JOB_TYPE_REMOTE).count()),
        ('Contract', user_apps.filter(job_type=JobApplication.JOB_TYPE_CONTRACT).count()),
    ])

    # 3. Monthly Trends (Past 6 months based on actual DB application_date)
    # Generate keys for last 6 months
    today = timezone.now().date()
    month_data = OrderedDict()
    for i in range(5, -1, -1):
        # Calculate year and month
        m = today.month - i
        y = today.year
        while m <= 0:
            m += 12
            y -= 1
        label = datetime(y, m, 1).strftime('%b %Y')
        month_data[label] = 0

    # Populate counts from user's records
    for app in user_apps:
        app_label = app.application_date.strftime('%b %Y')
        if app_label in month_data:
            month_data[app_label] += 1

    # 4. Conversion Rates
    interviewed = status_counts['Interview'] + status_counts['Selected']
    selected = status_counts['Selected']
    interview_rate = round((interviewed / total_count) * 100, 1) if total_count > 0 else 0
    selection_rate = round((selected / total_count) * 100, 1) if total_count > 0 else 0

    context = {
        'title': 'Analytics & Performance',
        'total_count': total_count,
        'status_counts': status_counts,
        'job_type_counts': job_type_counts,
        'interview_rate': interview_rate,
        'selection_rate': selection_rate,
        # JSON strings for Chart.js rendering
        'status_labels_json': json.dumps(list(status_counts.keys())),
        'status_values_json': json.dumps(list(status_counts.values())),
        'type_labels_json': json.dumps(list(job_type_counts.keys())),
        'type_values_json': json.dumps(list(job_type_counts.values())),
        'trend_labels_json': json.dumps(list(month_data.keys())),
        'trend_values_json': json.dumps(list(month_data.values())),
    }
    return render(request, 'jobs/analytics.html', context)
