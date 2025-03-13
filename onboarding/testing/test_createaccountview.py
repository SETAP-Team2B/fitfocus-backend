from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model
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
            'last_name': 'User '
        }
        response = self.client.post(self.url, data, content_type='application/json')
        self.assertEqual(response.status_code, 201)  # HTTP 201 Created
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
            'last_name': 'User '
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
            'last_name': 'User '
        }
        response = self.client.post(self.url, data, content_type='application/json')
        self.assertEqual(response.status_code, 400)  # HTTP 400 Bad Request
        self.assertIn("Invalid email or username.", response.json().get('error'))

    def test_create_account_missing_fields(self):
        data = {
            'email': 'test@example.com',
            'username': 'testuser',
            # 'password' is missing
            'first_name': 'Test',
            'last_name': 'User '
        }
        response = self.client.post(self.url, data, content_type='application/json')
        self.assertEqual(response.status_code, 400)  # HTTP 400 Bad Request
        self.assertIn("password is missing.", response.json().get('error'))

    def test_create_account_weak_password(self):
        data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': '123',  # Weak password
            'first_name': 'Test',
            'last_name': 'User '
        }
        response = self.client.post(self.url, data, content_type='application/json')
        self.assertEqual(response.status_code, 400)  # HTTP 400 Bad Request
        self.assertIn("Weak password.", response.json().get('error'))  # Adjust based on your error handling
