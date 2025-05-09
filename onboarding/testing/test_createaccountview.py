import json
from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework import status
from onboarding.models import VerifiedUser  
from onboarding.views import CreateAccountView

User  = get_user_model()

class CreateAccountViewTests(TestCase):
    """The Test Case for the CreateAccountView

    Contains tests for user creation functionality, ensuring correct responses to the functions
    """
    def setUp(self):
        """Sets up the Test Case

        Is called before each test to initialise the URL for the user creation end point

        :return: None
        """
        self.url = reverse('create-user')

    def test_create_account_success(self):
        """Test the successful creation of a user account

        Sends POST request with valid user data and verifies:\n
        - Response status code is OK (200)\n
        - Only one user is created in the database\n
        - The user email matches the input data

        :raises AssertationError: If any of the assertions fail
        :return: None
        """
        data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'StrongPassword123!',
            'first_name': 'Test',
            'last_name': 'User'
        }
        response = self.client.post(self.url, json.dumps(data), content_type='application/json')

        print("Response content:", response.content)  

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().email, 'test@example.com')

    def test_create_account_email_exists(self):
        """Tests account creation with existing email

        Creates a test user in database

        Sends POST request with same email and verifies:\n
        - Response status code is Bad Request (400)\n
        - Appropriate error message ("Email already exists on a user.")

        :raises AssertationError: If any of the assertions fail
        :return: None
        """
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

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST) 
        self.assertIn("Email already exists on a user.", json.loads(response.content).get('message'))

    def test_create_account_invalid_email(self):
        """Tests account creation with invalid email

        Sends POST request with invalid existing email and verifies:\n
        - Response status code is Bad Request (400)\n
        - Appropriate error message ("Invalid email or username.")

        :raises AssertationError: If any of the assertions fail
        :return: None
        """
        data = {
            'email': 'invalid-email',
            'username': 'testuser',
            'password': 'StrongPassword123!',
            'first_name': 'Test',
            'last_name': 'User '
        }
        response = self.client.post(self.url, data, content_type='application/json')

        print("Response content:", response.content)  

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Invalid email or username.", json.loads(response.content).get('message'))

    def test_create_account_missing_fields(self):
        """Tests account creation with missing fields

        Sends POST request with already missing password and verifies:\n
        - Response status code is Bad Request (400)\n
        - Appropriate error message ("'password' is missing.")

        :raises AssertationError: If any of the assertions fail
        :return: None
        """
        data = {
            'email': 'test@example.com',
            'username': 'testuser',
            # 'password' is missing
            'first_name': 'Test',
            'last_name': 'User'
        }
        response = self.client.post(self.url, data, content_type='application/json')

        print("Response content:", response.content)   

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("'password' is missing.", json.loads(response.content).get('message'))

    def test_create_account_weak_password(self):
        """Tests account creation with weak password

        Sends POST request with intentionlly weak password and verifies:\n
        - Response status code is Bad Request (400)\n
        - Appropriate error message ("Password is too weak. Use a strong password with at least 6 upper and lower case alpha-numeric characters including special symbols")

        :raises AssertationError: If any of the assertions fail
        :return: None
        """
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
