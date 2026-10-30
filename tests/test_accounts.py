"""
Test Suite for User Authentication and Profile Management (accounts app).
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User


class AccountsAuthenticationTests(TestCase):
    """
    Validates user registration, login, logout, password hashing, and profile updates.
    """

    def setUp(self):
        self.client = Client()
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.profile_url = reverse('profile')

        self.user_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'StrongPassword123!',
            'confirm_password': 'StrongPassword123!'
        }

    def test_user_registration_success(self):
        """User can register with valid credentials and password is encrypted."""
        response = self.client.post(self.register_url, data=self.user_data)
        # Should redirect to login page
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.login_url)

        # User must exist in the database
        user = User.objects.filter(username='testuser').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.email, 'testuser@example.com')
        # Password must be hashed, NOT stored plaintext
        self.assertNotEqual(user.password, 'StrongPassword123!')
        self.assertTrue(user.check_password('StrongPassword123!'))

    def test_registration_mismatched_passwords(self):
        """Registration fails when password and confirm_password do not match."""
        invalid_data = self.user_data.copy()
        invalid_data['confirm_password'] = 'DifferentPassword456!'

        response = self.client.post(self.register_url, data=invalid_data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='testuser').exists())
        self.assertFormError(response, 'form', 'confirm_password', 'Passwords do not match. Please re-enter.')

    def test_registration_duplicate_email(self):
        """Registration fails when the email is already in use."""
        User.objects.create_user(
            username='existinguser',
            email='testuser@example.com',
            password='Password123!'
        )

        response = self.client.post(self.register_url, data=self.user_data)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'email', 'An account with this email address already exists.')

    def test_user_login_success(self):
        """Registered user can log in with valid credentials."""
        User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='StrongPassword123!'
        )

        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'StrongPassword123!'
        })
        # Successful login redirects
        self.assertEqual(response.status_code, 302)

    def test_user_login_invalid_credentials(self):
        """Login fails when given invalid password."""
        User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='StrongPassword123!'
        )

        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'WrongPassword!'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid username or password")

    def test_user_logout(self):
        """Logged-in user can log out successfully."""
        user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='StrongPassword123!'
        )
        self.client.force_login(user)

        response = self.client.get(self.logout_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.login_url)

    def test_profile_requires_login(self):
        """Unauthenticated user attempting to access profile is redirected to login."""
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(self.login_url, response.url)

    def test_profile_update_success(self):
        """Authenticated user can update profile details."""
        user = User.objects.create_user(
            username='testuser',
            email='old@example.com',
            first_name='OldFirst',
            last_name='OldLast',
            password='StrongPassword123!'
        )
        self.client.force_login(user)

        update_data = {
            'first_name': 'NewFirst',
            'last_name': 'NewLast',
            'email': 'newemail@example.com'
        }
        response = self.client.post(self.profile_url, data=update_data)
        self.assertEqual(response.status_code, 302)

        user.refresh_from_db()
        self.assertEqual(user.first_name, 'NewFirst')
        self.assertEqual(user.last_name, 'NewLast')
        self.assertEqual(user.email, 'newemail@example.com')
