"""
Jobs App Views for JobTrack.

Implements complete CRUD operations for job applications,
search, multi-criteria filtering, sorting, pagination, and user isolation.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from .models import JobApplication
from .forms import JobApplicationForm


@login_required
def job_list_view(request):
    """
    Display a list of job applications belonging strictly to the logged-in user.
    Supports:
    - Text search by company name, job title, and location.
    - Filtering by application status (Applied, Shortlisted, etc.).
    - Filtering by job type (Full Time, Remote, etc.).
    - Sorting by application date (newest or oldest) and company name.
    - Clean pagination (10 applications per page).
    """
    # Base query restricted strictly to current user's records
    applications = JobApplication.objects.filter(user=request.user)

    # Search filter
    search_query = request.GET.get('q', '').strip()
    if search_query:
        applications = applications.filter(
            Q(company_name__icontains=search_query) |
            Q(job_title__icontains=search_query) |
            Q(job_location__icontains=search_query)
        )

    # Status filter
    status_filter = request.GET.get('status', '').strip()
    if status_filter:
        applications = applications.filter(application_status=status_filter)

    # Job type filter
    job_type_filter = request.GET.get('job_type', '').strip()
    if job_type_filter:
        applications = applications.filter(job_type=job_type_filter)

    # Sorting
    sort_by = request.GET.get('sort', '-application_date').strip()
    valid_sorts = {
        '-application_date': '-application_date',
        'application_date': 'application_date',
        'company_name': 'company_name',
        '-company_name': '-company_name',
    }
    applications = applications.order_by(valid_sorts.get(sort_by, '-application_date'))

    # Pagination: 10 per page
    paginator = Paginator(applications, 10)
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.get_page(page_number)
    except (PageNotAnInteger, EmptyPage):
        page_obj = paginator.get_page(1)

    context = {
        'title': 'Job Applications',
        'page_obj': page_obj,
        'applications': page_obj.object_list,
        'search_query': search_query,
        'status_filter': status_filter,
        'job_type_filter': job_type_filter,
        'sort_by': sort_by,
        'status_choices': JobApplication.STATUS_CHOICES,
        'job_type_choices': JobApplication.JOB_TYPE_CHOICES,
        'total_filtered_count': applications.count(),
    }
    return render(request, 'jobs/job_list.html', context)


@login_required
def job_detail_view(request, pk):
    """
    Display comprehensive details of an individual job application.
    Enforces user data isolation: 404 is returned if another user attempts access.
    """
    application = get_object_or_404(JobApplication, pk=pk, user=request.user)
    interviews = application.interviews.all().order_by('-interview_date')

    context = {
        'title': f"{application.job_title} - {application.company_name}",
        'application': application,
        'interviews': interviews,
    }
    return render(request, 'jobs/job_detail.html', context)


@login_required
def job_create_view(request):
    """
    Handle adding a new job application.
    Automatically assigns the application to request.user.
    """
    if request.method == 'POST':
        form = JobApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user
            application.save()
            messages.success(
                request,
                f"Application for '{application.job_title}' at {application.company_name} added successfully!"
            )
            return redirect('job_detail', pk=application.pk)
        else:
            messages.error(request, "Please correct the errors in the form below.")
    else:
        form = JobApplicationForm()

    context = {
        'title': 'Add Job Application',
        'form': form,
        'action_verb': 'Add',
    }
    return render(request, 'jobs/job_form.html', context)


@login_required
def job_update_view(request, pk):
    """
    Handle updating an existing job application owned by the user.
    """
    application = get_object_or_404(JobApplication, pk=pk, user=request.user)

    if request.method == 'POST':
        form = JobApplicationForm(request.POST, instance=application)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                f"Application for '{application.job_title}' at {application.company_name} updated successfully!"
            )
            return redirect('job_detail', pk=application.pk)
        else:
            messages.error(request, "Please correct the errors in the form below.")
    else:
        form = JobApplicationForm(instance=application)

    context = {
        'title': f"Edit {application.job_title}",
        'form': form,
        'application': application,
        'action_verb': 'Update',
    }
    return render(request, 'jobs/job_form.html', context)


@login_required
def job_delete_view(request, pk):
    """
    Handle deletion of a job application owned by the user with confirmation.
    """
    application = get_object_or_404(JobApplication, pk=pk, user=request.user)

    if request.method == 'POST':
        company_name = application.company_name
        job_title = application.job_title
        application.delete()
        messages.success(request, f"Application for '{job_title}' at {company_name} was deleted successfully.")
        return redirect('job_list')

    context = {
        'title': f"Delete Application - {application.job_title}",
        'application': application,
    }
    return render(request, 'jobs/job_confirm_delete.html', context)


# Placeholder views for dashboard and analytics (fully wired in Stage 5)
@login_required
def dashboard_view(request):
    """Dashboard view (implemented in Stage 5)."""
    from . import views_dashboard
    return views_dashboard.dashboard_view(request)


@login_required
def analytics_view(request):
    """Analytics view (implemented in Stage 5)."""
    from . import views_dashboard
    return views_dashboard.analytics_view(request)
