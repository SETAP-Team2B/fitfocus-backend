import json
import unittest
from django.urls import reverse
from django.test import Client
from onboarding.models import user, verified
from onboarding.views import CreateAccountView  # Import your view class

class CreateAccountViewTests(unittest.TestCase):
    def setUp(self):
        self.client = Client()  # Create a test client
        self.url = reverse('create-user')  # Adjust the URL name based on your URL configuration

    def test_create_account_success(self):
        data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'StrongPassword123!',
            'first_name': 'Test',
            'last_name': 'User  '
        }
        response = self.client.post(self.url, data, content_type='application/json')
        self.assertEqual(response.status_code, 201)  # HTTP 201 Created
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(Verified.objects.count(), 1)

    def test_create_account_duplicate_email(self):
        User.objects.create_user(email='test@example.com', username='testuser', password='StrongPassword123!')
        data = {
            'email': 'test@example.com',
            'username': 'newuser',
            'password': 'StrongPassword123!',
            'first_name': 'New',
            'last_name': 'User  '
        }
        response = self.client.post(self.url, data, content_type='application/json')
        self.assertEqual(response.status_code, 400)  # HTTP 400 Bad Request
        self.assertIn("Email already exists on a user.", response.json().get('error'))

    def test_create_account_invalid_email(self):
        data = {
            'email': 'invalid-email',
            'username': 'testuser',
            'password': 'StrongPassword123!',
            'first_name': 'Test',
            'last_name': 'User  '
        }
        response = self.client.post(self.url, data, content_type='application/json')
        self.assertEqual(response.status_code, 400)  # HTTP 400 Bad Request
        self.assertIn("Invalid email or username.", response.json().get('error'))
    def test_create_account_missing_fields(self):
        data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'first_name': 'Test'
            # Missing password and last_name
        }
        response = self.client.post(self.url, data, content_type='application/json')
        self.assertEqual(response.status_code, 400)  # HTTP 400 Bad Request
        self.assertIn("password is missing.", response.json().get('error'))

    def test_create_account_weak_password(self):
        data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'weak',  # Weak password
            'first_name': 'Test',
            'last_name': 'User  '
        }
        response = self.client.post(self.url, data, content_type='application/json')
        self.assertEqual(response.status_code, 400)  # HTTP 400 Bad Request
        self.assertIn("Weak password", response.json().get('error'))  # Adjust based on your error handling

    def test_create_account_invalid_name(self):
        data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'StrongPassword123!',
            'first_name': 'InvalidName123',  # Invalid name
            'last_name': 'User  '
        }
        response = self.client.post(self.url, data, content_type='application/json')
        self.assertEqual(response.status_code, 400)  # HTTP 400 Bad Request
        self.assertIn("Invalid name", response.json().get('error'))  # Adjust based on your error handling

    def test_create_account_invalid_request_type(self):
        response = self.client.post(self.url, data='not-a-dict', content_type='application/json')
        self.assertEqual(response.status_code, 400)  # HTTP 400 Bad Request
        self.assertIn("Invalid request type.", response.json().get('error'))

     def test_create_account_username_exists(self):
        User.objects.create_user(email='test@example.com', username='testuser', password='StrongPassword123!')
        data = {
            'email': 'new@example.com',
            'username': 'testuser',  # Duplicate username
            'password': 'StrongPassword123!',
            'first_name': 'New',
            'last_name': 'User  '
        }
        response = self.client.post(self.url, data, content_type='application/json')
        self.assertEqual(response.status_code, 400)  # HTTP 400 Bad Request
        self.assertIn("Username already exists. Please try again.", response.json().get('error'))  # Adjust based on your error handling
