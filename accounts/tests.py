from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase


class AccountAuthTests(APITestCase):
    """
    Test suite for user registration, login, logout, and token authentication.
    """

    def setUp(self):
        self.register_url = reverse('accounts:register')
        self.login_url = reverse('accounts:login')
        self.logout_url = reverse('accounts:logout')
        self.profile_url = reverse('accounts:profile')

        self.user_data = {
            'username': 'john_doe',
            'email': 'john@example.com',
            'password': 'SecurePassword123!',
            'password2': 'SecurePassword123!',
            'first_name': 'John',
            'last_name': 'Doe',
        }
        self.existing_user = User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='TestPassword123!'
        )
        self.token = Token.objects.create(user=self.existing_user)

    def test_user_registration_success(self):
        """Test successful registration returns user data and auth token."""
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['username'], 'john_doe')
        self.assertEqual(response.data['user']['email'], 'john@example.com')
        # Check token exists in database
        self.assertTrue(Token.objects.filter(key=response.data['token']).exists())

    def test_registration_password_mismatch(self):
        """Test registration fails when password and confirm password do not match."""
        invalid_data = self.user_data.copy()
        invalid_data['password2'] = 'DifferentPassword123!'
        response = self.client.post(self.register_url, invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password2', response.data)

    def test_registration_duplicate_username(self):
        """Test registration fails with an already existing username."""
        invalid_data = self.user_data.copy()
        invalid_data['username'] = 'existinguser'
        response = self.client.post(self.register_url, invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)

    def test_registration_duplicate_email(self):
        """Test registration fails with an already registered email."""
        invalid_data = self.user_data.copy()
        invalid_data['email'] = 'existing@example.com'
        response = self.client.post(self.register_url, invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_login_success(self):
        """Test login with valid credentials returns auth token."""
        login_data = {
            'username': 'existinguser',
            'password': 'TestPassword123!',
        }
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['token'], self.token.key)

    def test_login_invalid_password(self):
        """Test login fails with incorrect password."""
        login_data = {
            'username': 'existinguser',
            'password': 'WrongPassword!',
        }
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_missing_fields(self):
        """Test login fails if required fields are missing."""
        response = self.client.post(self.login_url, {'username': 'existinguser'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_logout_authenticated(self):
        """Test authenticated user can log out and their token is deleted."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Token.objects.filter(key=self.token.key).exists())

    def test_logout_unauthenticated(self):
        """Test unauthenticated user cannot call logout endpoint."""
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_profile_authenticated(self):
        """Test authenticated user can access profile."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'existinguser')

    def test_get_profile_unauthenticated(self):
        """Test unauthenticated user cannot access profile endpoint."""
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_obtain_auth_token_endpoint(self):
        """Test obtaining token via standard DRF /api-token-auth/ endpoint."""
        response = self.client.post('/api-token-auth/', {
            'username': 'existinguser',
            'password': 'TestPassword123!'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['token'], self.token.key)

