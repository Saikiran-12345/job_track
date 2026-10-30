"""
Jobs App Views (Dashboard and Job Application CRUD).
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


@login_required
def dashboard_view(request):
    """Placeholder dashboard view."""
    return render(request, 'jobs/dashboard.html', {'title': 'Dashboard'})


@login_required
def job_list_view(request):
    """Placeholder job list view."""
    return render(request, 'jobs/job_list.html', {'title': 'Job Applications'})


@login_required
def job_create_view(request):
    """Placeholder job create view."""
    return render(request, 'jobs/job_form.html', {'title': 'Add Job Application'})


@login_required
def analytics_view(request):
    """Placeholder analytics view."""
    return render(request, 'jobs/analytics.html', {'title': 'Analytics'})
