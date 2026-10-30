"""
JobTrack Root URL Configuration.

Routes traffic to modular apps:
- accounts: Authentication & Profile management
- jobs: Job Applications & Dashboard
- interviews: Interview Scheduling & Tracking
- api: Django REST Framework API endpoints
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('', include('jobs.urls')),
    path('interviews/', include('interviews.urls')),
    path('api/', include('api.urls')),
]
