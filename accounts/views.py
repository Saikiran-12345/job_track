"""
Accounts Views for JobTrack.

Handles user registration, login, logout, and profile management.
All views follow clean Django conventions and provide user-friendly feedback.
"""

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, UserLoginForm, UserProfileForm


def register_view(request):
    """
    Handle user registration.
    Redirects already authenticated users to the dashboard.
    On valid submission, creates a new user with securely hashed password.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(
                request,
                f"Account created successfully for {user.username}! You can now log in."
            )
            return redirect('login')
        else:
            messages.error(request, "Please correct the errors below to complete registration.")
    else:
        form = UserRegisterForm()

    return render(request, 'accounts/register.html', {'form': form, 'title': 'Register'})


def login_view(request):
    """
    Handle user login using Django's built-in AuthenticationForm.
    Redirects already authenticated users to the dashboard.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            
            # Support redirecting back to the originally requested page
            next_url = request.GET.get('next') or request.POST.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password. Please try again.")
    else:
        form = UserLoginForm()

    return render(request, 'accounts/login.html', {'form': form, 'title': 'Login'})


def logout_view(request):
    """
    Handle user logout and invalidate the current session.
    """
    if request.user.is_authenticated:
        logout(request)
        messages.info(request, "You have been logged out successfully. See you soon!")
    return redirect('login')


@login_required
def profile_view(request):
    """
    Display and update the logged-in user's profile information.
    Provides personal metrics (e.g. total applications created).
    """
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile details have been updated successfully!")
            return redirect('profile')
        else:
            messages.error(request, "Please correct the errors in the profile form.")
    else:
        form = UserProfileForm(instance=request.user)

    # Calculate user statistics safely (handling if JobApplication model is registered)
    total_apps = getattr(request.user, 'job_applications', None)
    app_count = total_apps.count() if total_apps is not None else 0

    context = {
        'form': form,
        'title': 'User Profile',
        'application_count': app_count,
    }
    return render(request, 'accounts/profile.html', context)
