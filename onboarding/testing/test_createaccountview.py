import json
from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework import status
from onboarding.models import VerifiedUser  
from onboarding.views import CreateAccountView

User  = get_user_model()

class CreateAccountViewTests(TestCase):
    def setUp(self):
        self.url = reverse('create-user')

    def test_create_account_success(self):
        data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'StrongPassword123!',
            'first_name': 'Test',
            'last_name': 'User'
        }
        response = self.client.post(self.url, json.dumps(data), content_type='application/json')

        print("Response content:", response.content)  

        self.assertEqual(response.status_code, 200)  # HTTP 201 Created
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().email, 'test@example.com')

    def test_create_account_email_exists(self):
        User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='StrongPassword123!'
        )
        data = {
            'email': 'test@example.com',
            'username': 'newuser',
            'password': 'StrongPassword123!',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = self.client.post(self.url, data, content_type='application/json')

        print("Response content:", response.content)  

        self.assertEqual(response.status_code, 400)  # HTTP 400 Bad Request
        self.assertIn("Email already exists on a user.", json.loads(response.content).get('message'))

    def test_create_account_invalid_email(self):
        data = {
            'email': 'invalid-email',
            'username': 'testuser',
            'password': 'StrongPassword123!',
            'first_name': 'Test',
            'last_name': 'User '
        }
        response = self.client.post(self.url, data, content_type='application/json')

        print("Response content:", response.content)  

        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid email or username.", json.loads(response.content).get('message'))

    def test_create_account_missing_fields(self):
        data = {
            'email': 'test@example.com',
            'username': 'testuser',
            # 'password' is missing
            'first_name': 'Test',
            'last_name': 'User'
        }
        response = self.client.post(self.url, data, content_type='application/json')

        print("Response content:", response.content)   

        self.assertEqual(response.status_code, 400)  # HTTP 400 Bad Request
        self.assertIn("'password' is missing.", json.loads(response.content).get('message'))

    def test_create_account_weak_password(self):
        data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'password': '123'  # Intentionally weak password
        }
        response = self.client.post(self.url, json.dumps(data), content_type='application/json')

        print("Response content:", response.content)  

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)  
        self.assertIn("Password is too weak. Use a strong password with at least 6 upper and lower case alpha-numeric characters including special symbols", json.loads(response.content).get('message'))
