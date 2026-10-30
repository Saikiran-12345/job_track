"""
Interviews URL Configuration.
"""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.interview_list_view, name='interview_list'),
]
