"""
Interviews App Views for JobTrack.

Handles scheduling, updating, viewing, and deleting interview rounds
with strict user isolation and automatic application status updates.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Interview
from .forms import InterviewForm
from jobs.models import JobApplication


@login_required
def interview_list_view(request):
    """
    Display a list of scheduled and completed interviews for the logged-in user.
    Supports filtering by 'all', 'upcoming', and 'completed'.
    """
    interviews = Interview.objects.filter(
        job_application__user=request.user
    ).select_related('job_application')

    tab_filter = request.GET.get('tab', 'all')
    now = timezone.now()

    if tab_filter == 'upcoming':
        interviews = interviews.filter(interview_date__gte=now, status='Scheduled').order_by('interview_date')
    elif tab_filter == 'completed':
        interviews = interviews.filter(status='Completed').order_by('-interview_date')
    else:
        interviews = interviews.order_by('-interview_date')

    context = {
        'title': 'Interview Management',
        'interviews': interviews,
        'tab_filter': tab_filter,
        'upcoming_count': Interview.objects.filter(
            job_application__user=request.user,
            interview_date__gte=now,
            status='Scheduled'
        ).count(),
        'total_count': Interview.objects.filter(job_application__user=request.user).count(),
    }
    return render(request, 'interviews/interview_list.html', context)


@login_required
def interview_create_view(request):
    """
    Schedule an interview across any of the user's active applications.
    """
    # Check if user has any job applications first
    has_apps = JobApplication.objects.filter(user=request.user).exists()
    if not has_apps:
        messages.warning(
            request,
            "You need to create at least one Job Application before scheduling an interview."
        )
        return redirect('job_create')

    if request.method == 'POST':
        form = InterviewForm(request.POST, user=request.user)
        if form.is_valid():
            interview = form.save(commit=False)
            # Security verification: Ensure the selected job application belongs to the logged-in user
            if interview.job_application.user != request.user:
                messages.error(request, "Unauthorized action.")
                return redirect('dashboard')

            interview.save()

            # Automatic lifecycle progression: If job was 'Applied', update to 'Interview'
            if interview.job_application.application_status == JobApplication.STATUS_APPLIED:
                interview.job_application.application_status = JobApplication.STATUS_INTERVIEW
                interview.job_application.save(update_fields=['application_status'])

            messages.success(
                request,
                f"{interview.interview_round} interview scheduled successfully for {interview.job_application.company_name}!"
            )
            return redirect('job_detail', pk=interview.job_application.pk)
        else:
            messages.error(request, "Please correct the errors in the form below.")
    else:
        form = InterviewForm(user=request.user)

    context = {
        'title': 'Schedule Interview',
        'form': form,
        'action_verb': 'Schedule',
    }
    return render(request, 'interviews/interview_form.html', context)


@login_required
def interview_create_for_job_view(request, job_pk):
    """
    Schedule an interview directly for a specific job application.
    """
    application = get_object_or_404(JobApplication, pk=job_pk, user=request.user)

    if request.method == 'POST':
        form = InterviewForm(request.POST, user=request.user)
        if form.is_valid():
            interview = form.save(commit=False)
            interview.job_application = application
            interview.save()

            # Progress application status if appropriate
            if application.application_status == JobApplication.STATUS_APPLIED:
                application.application_status = JobApplication.STATUS_INTERVIEW
                application.save(update_fields=['application_status'])

            messages.success(
                request,
                f"{interview.interview_round} interview scheduled for {application.company_name}!"
            )
            return redirect('job_detail', pk=application.pk)
        else:
            messages.error(request, "Please correct the errors in the form below.")
    else:
        form = InterviewForm(user=request.user, initial_job=application)

    context = {
        'title': f"Schedule Interview - {application.company_name}",
        'form': form,
        'application': application,
        'action_verb': 'Schedule',
    }
    return render(request, 'interviews/interview_form.html', context)


@login_required
def interview_update_view(request, pk):
    """
    Update details, status, or feedback for an existing interview.
    """
    interview = get_object_or_404(
        Interview,
        pk=pk,
        job_application__user=request.user
    )

    if request.method == 'POST':
        form = InterviewForm(request.POST, instance=interview, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                f"Interview details updated for {interview.job_application.company_name}!"
            )
            return redirect('job_detail', pk=interview.job_application.pk)
        else:
            messages.error(request, "Please correct the errors in the form below.")
    else:
        form = InterviewForm(instance=interview, user=request.user)

    context = {
        'title': f"Edit Interview - {interview.job_application.company_name}",
        'form': form,
        'interview': interview,
        'action_verb': 'Update',
    }
    return render(request, 'interviews/interview_form.html', context)


@login_required
def interview_delete_view(request, pk):
    """
    Delete an interview with confirmation.
    """
    interview = get_object_or_404(
        Interview,
        pk=pk,
        job_application__user=request.user
    )
    job_pk = interview.job_application.pk

    if request.method == 'POST':
        interview.delete()
        messages.success(request, "Interview record removed successfully.")
        return redirect('job_detail', pk=job_pk)

    context = {
        'title': 'Delete Interview',
        'interview': interview,
    }
    return render(request, 'interviews/interview_confirm_delete.html', context)
