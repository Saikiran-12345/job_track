"""
Interviews URL Configuration.
"""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.interview_list_view, name='interview_list'),
    path('new/', views.interview_create_view, name='interview_create'),
    path('new/<int:job_pk>/', views.interview_create_for_job_view, name='interview_create_for_job'),
    path('<int:pk>/edit/', views.interview_update_view, name='interview_update'),
    path('<int:pk>/delete/', views.interview_delete_view, name='interview_delete'),
]
