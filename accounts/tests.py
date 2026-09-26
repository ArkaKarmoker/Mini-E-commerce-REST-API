from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase


class AccountAuthTests(APITestCase):
    """
    Core test suite for User Authentication: Registration, Login, Token Lifecycle, and Profile.
    """

    def setUp(self):
        self.register_url = reverse('accounts:register')
        self.login_url = reverse('accounts:login')
        self.logout_url = reverse('accounts:logout')
        self.profile_url = reverse('accounts:profile')

        self.user = User.objects.create_user(
            username='existing_user',
            email='existing@example.com',
            password='Password123!'
        )
        self.token = Token.objects.create(user=self.user)

    def test_user_registration(self):
        """1. Register a new user and receive auth token."""
        payload = {
            'username': 'new_user',
            'email': 'new_user@example.com',
            'password': 'SecurePassword123!',
            'password2': 'SecurePassword123!',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = self.client.post(self.register_url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['user']['username'], 'new_user')

    def test_user_login(self):
        """2. Login with username & password to obtain auth token."""
        response = self.client.post(self.login_url, {
            'username': 'existing_user',
            'password': 'Password123!'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['token'], self.token.key)

    def test_protected_profile_access(self):
        """3. Access protected APIs using token (unauthenticated fails with 401)."""
        # Unauthenticated request fails
        unauth_resp = self.client.get(self.profile_url)
        self.assertEqual(unauth_resp.status_code, status.HTTP_401_UNAUTHORIZED)

        # Authenticated request succeeds
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        auth_resp = self.client.get(self.profile_url)
        self.assertEqual(auth_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(auth_resp.data['username'], 'existing_user')

    def test_user_logout(self):
        """4. Logout deletes and invalidates the active auth token."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Token.objects.filter(key=self.token.key).exists())
