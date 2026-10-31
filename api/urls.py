"""
API App URL Configuration.

Wires DRF DefaultRouter for JobApplication and Interview ViewSets,
along with custom endpoints for Dashboard analytics and User profile.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('applications', views.JobApplicationViewSet, basename='api-application')
router.register('interviews', views.InterviewViewSet, basename='api-interview')

urlpatterns = [
    path('dashboard/', views.DashboardStatsAPIView.as_view(), name='api-dashboard'),
    path('user/', views.CurrentUserProfileAPIView.as_view(), name='api-user'),
    path('', include(router.urls)),
]
