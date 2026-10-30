"""
Jobs App URL Configuration.
"""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('applications/', views.job_list_view, name='job_list'),
    path('applications/new/', views.job_create_view, name='job_create'),
    path('analytics/', views.analytics_view, name='analytics'),
]
