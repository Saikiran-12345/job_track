"""
Interviews Admin Configuration.
"""

from django.contrib import admin
from .models import Interview


@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):
    list_display = (
        'interview_round',
        'job_application',
        'interview_date',
        'status',
        'created_at',
    )
    list_filter = ('interview_round', 'status', 'interview_date')
    search_fields = (
        'job_application__company_name',
        'job_application__job_title',
        'notes_or_feedback',
        'location_or_link',
    )
    ordering = ('-interview_date',)
    readonly_fields = ('created_at', 'updated_at')
