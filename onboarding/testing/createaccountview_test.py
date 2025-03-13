from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from onboarding.models import verified, user 

class CreateAccountViewTests(APITestCase):
    def setUp(self):
        self.url = reverse('create-user') 

    def test_create_account_success(self):
        data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'StrongPassword123!',
            'first_name': 'Test',
            'last_name': 'user '
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(user.objects.count(), 1)
        self.assertEqual(verified.objects.count(), 1)

    def test_create_account_duplicate_email(self):
        user.objects.create_user(email='test@example.com', username='testuser', password='StrongPassword123!')
        data = {
            'email': 'test@example.com',
            'username': 'newuser',
            'password': 'StrongPassword123!',
            'first_name': 'New',
            'last_name': 'User '
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Email already exists on a user.", response.data['error'])

    def test_create_account_invalid_email(self):
        data = {
            'email': 'invalid-email',
            'username': 'testuser',
            'password': 'StrongPassword123!',
            'first_name': 'Test',
            'last_name': 'User '
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Invalid email or username.", response.data['error'])

    def test_create_account_missing_fields(self):
        data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'first_name': 'Test'
            # Missing password and last_name
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password is missing.", response.data['error'])

    def test_create_account_weak_password(self):
        data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'weak',  # Weak password
            'first_name': 'Test',
            'last_name': 'User '
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Weak password", response.data['error'])  # Adjust based on your error handling

    def test_create_account_invalid_name(self):
        data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'StrongPassword123!',
            'first_name': 'InvalidName123',  # Invalid name
            'last_name': 'User '
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Invalid name", response.data['error'])  # Adjust based on your error handling
