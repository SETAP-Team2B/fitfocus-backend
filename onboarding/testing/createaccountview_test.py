from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch
from models import User, VerifiedUser   # Adjust based on your project structure

class CreateAccountViewTest(APITestCase):
    def setUp(self):
        self.url = reverse('create-account')  # Replace with the actual URL name for your view

    @patch('your_app.views.validate_email')  # Adjust the import path
    @patch('your_app.views.validate_username')  # Adjust the import path
    @patch('your_app.views.check_name')  # Adjust the import path
    @patch('your_app.views.check_password')  # Adjust the import path
    def test_create_account_success(self, mock_check_password, mock_check_name, mock_validate_username, mock_validate_email):
        # Mock the validation functions
        mock_validate_email.return_value = True
        mock_validate_username.return_value = True
        mock_check_name.side_effect = lambda x: x  # Just return the name as is
        mock_check_password.return_value = 'hashed_password'  # Mock hashed password

        # Prepare a valid request
        request_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'StrongPassword123!',
            'first_name': 'Test',
            'last_name': 'User '
        }

        # Make the POST request
        response = self.client.post(self.url, data=request_data)

        # Check that the response is successful
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['email'], 'test@example.com')
        self.assertEqual(response.data['username'], 'testuser')

        # Check that the user was created
        user = User.objects.get(email='test@example.com')
        self.assertIsNotNone(user)
        self.assertEqual(user.username, 'testuser')

        # Check that the VerifiedUser  instance was created
        verified_user = VerifiedUser .objects.get(user=user)
        self.assertIsNotNone(verified_user)

    @patch('your_app.views.validate_email')
    @patch('your_app.views.validate_username')
    def test_create_account_email_exists(self, mock_validate_username, mock_validate_email):
        # Create a user to test against
        User.objects.create_user(email='test@example.com', password='password', username='testuser')

        # Mock the validation functions
        mock_validate_email.return_value = True
        mock_validate_username.return_value = True

        # Prepare a request with an existing email
        request_data = {
            'email': 'test@example.com',
            'username': 'newuser',
            'password': 'StrongPassword123!',
            'first_name': 'New',
            'last_name': 'User '
        }

        # Make the POST request
        response = self.client.post(self.url, data=request_data)

        # Check that the response indicates an error
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Email already exists on a user.", response.data['error'])

    @patch('your_app.views.validate_email')
    @patch('your_app.views.validate_username')
    def test_create_account_missing_fields(self, mock_validate_username, mock_validate_email):
        # Mock the validation functions
        mock_validate_email.return_value = True
        mock_validate_username.return_value = True

        # Prepare a request with missing fields
        request_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            # 'password' is missing
            'first_name': 'Test',
            'last_name': 'User '
        }

        # Make the POST request
        response = self.client.post(self.url, data=request_data)

        # Check that the response indicates an error
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password is missing.", response.data['error'])
