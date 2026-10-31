"""
Jobs Admin Configuration.
"""

from django.contrib import admin
from .models import JobApplication


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = (
        'job_title',
        'company_name',
        'user',
        'job_type',
        'application_status',
        'application_date',
        'created_at'
    )
    list_filter = ('application_status', 'job_type', 'application_date', 'user')
    search_fields = ('company_name', 'job_title', 'job_location', 'user__username')
    ordering = ('-application_date', '-created_at')
    readonly_fields = ('created_at', 'updated_at')
