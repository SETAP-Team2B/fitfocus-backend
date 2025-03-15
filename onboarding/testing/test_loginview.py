import json
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch
from django.contrib.auth.models import User
from onboarding.models import VerifiedUser   # Adjust the import based on your project structure
from django.contrib.auth import get_user_model

class LoginViewTests(APITestCase):
    def setUp(self):
        self.url = reverse('login-user')  # Adjust the URL name based on your URL configuration
        self.user_username = 'testuser'
        self.user_email = 'test@example.com'
        self.user_password = 'OldPassword123!'  # Use a strong password
        
        # Create a user instance
        self.user = User.objects.create_user(
            username=self.user_username,
            email=self.user_email,
            password=self.user_password            
        )

        # Create a VerifiedUser  instance and set it as verified
        self.verified_user = VerifiedUser (
            user=self.user,
            verified=True  # Mark the user as verified
        )
        self.verified_user.save() 

    def test_login_success(self):
        data = {
            'username': self.user_username,
            'password': self.user_password,
        }
        response = self.client.post(self.url, json.dumps(data), content_type='application/json')  # Use format='json' for JSON requests

        # Print the response content for debugging
        print("Response content:", response.content)

        # Check the response status code
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch('onboarding.views.get_tokens_for_user')
    def test_missing_credentials(self, mock_get_tokens):
        data = {
            'username': 'testuser',  # Missing password
        }
        response = self.client.post(self.url, data, format='json')
        
        print("Response content:", response.content)  # Debugging output

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Username/Email and password are required", json.loads(response.content).get('message'))

    @patch('onboarding.views.get_tokens_for_user')
    def test_user_not_found(self, mock_get_tokens):
        data = {
            'username': 'nonexistentuser',
            'password': 'somepassword',
        }
        response = self.client.post(self.url, data, format='json')
        
        print("Response content:", response.content)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Invalid username or password.", json.loads(response.content).get('message'))

    @patch('onboarding.views.get_tokens_for_user')
    def test_multiple_users_found(self, mock_get_tokens):
        # Create another user with the same email
        User.objects.create_user(
            username='anotheruser',
            email=self.user_email,
            password='AnotherPassword123!'
        )

        data = {
            'email': self.user_email,
            'password': self.user_password,
        }
        response = self.client.post(self.url, data, format='json')
        
        print("Response content:", response.content)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Multiple users found with given email.", json.loads(response.content).get('message'))

    @patch('onboarding.views.get_tokens_for_user')
    def test_incorrect_password(self, mock_get_tokens):
        data = {
            'username': 'testuser',
            'password': 'wrongpassword',  # Incorrect password
        }
        response = self.client.post(self.url, json.dumps(data), content_type='application/json')
        
        print("Response content:", response.content)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Invalid username or password.", json.loads(response.content).get('message'))

    def test_unverified_user(self):
        # Create a new user that is not verified
        unverified_user = get_user_model().objects.create_user(
            username='unverifieduser',
            email='unverified@example.com',
            password='AnotherPassword123!'
        )
        VerifiedUser.objects.create(user=unverified_user, verified=False)  # Mark as unverified

        data = {
            'username': 'unverifieduser',
            'password': 'AnotherPassword123!',
        }
        response = self.client.post(self.url, json.dumps(data), content_type='application/json')

        print("Response content:", response.content)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("User not verified.", json.loads(response.content).get('message'))
