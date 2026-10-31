"""
Jobs URL Configuration.
"""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('applications/', views.job_list_view, name='job_list'),
    path('applications/new/', views.job_create_view, name='job_create'),
    path('applications/<int:pk>/', views.job_detail_view, name='job_detail'),
    path('applications/<int:pk>/edit/', views.job_update_view, name='job_update'),
    path('applications/<int:pk>/delete/', views.job_delete_view, name='job_delete'),
    path('analytics/', views.analytics_view, name='analytics'),
]
