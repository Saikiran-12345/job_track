"""
Interviews App Views.
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def interview_list_view(request):
    """Placeholder interview list view."""
    return render(request, 'interviews/interview_list.html', {'title': 'Interviews'})
