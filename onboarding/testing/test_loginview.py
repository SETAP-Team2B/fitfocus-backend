import json
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch
from django.contrib.auth.models import User
from onboarding.models import VerifiedUser   
from django.contrib.auth import get_user_model

class LoginViewTests(APITestCase):
    """Test Case for the LoginView

    Contains tests for the login functionality of users, ensuring the correct responses to functions
    """
    def setUp(self):
        """Sets up the Test Case 
       
        Is called before each test to initialize the URL for the login endpoint 
        
        Creates a test User and a VerifiedUser

        :return: None
        """
        self.url = reverse('login-user')  
        self.user_username = 'testuser'
        self.user_email = 'test@example.com'
        self.user_password = 'OldPassword123!'  
        
        # Create a user instance
        self.user = User.objects.create_user(
            username=self.user_username,
            email=self.user_email,
            password=self.user_password            
        )

        # Create a VerifiedUser instance and set it as verified
        self.verified_user = VerifiedUser (
            user=self.user,
            verified=True  # Mark the user as verified
        )
        self.verified_user.save() 

    def test_login_success(self):
        """Tests successful login 

        Sends a POST request with valid username and password and verifies:\n
        - Response status code is OK (200)
        
        :raises AssertationError: If any of the assertions fail
        :return: None
        """
        data = {
            'username': self.user_username,
            'password': self.user_password,
        }
        response = self.client.post(self.url, json.dumps(data), content_type='application/json') 

        print("Response content:", response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch('onboarding.views.get_tokens_for_user')
    def test_missing_credentials(self, mock_get_tokens):
        """Tests login with missing data

        Sends a POST request missing a password and verifies:\n 
        - Response status code is Bad Request (400)\n 
        - Appropriate error message ("Username/Email and password are required")

        :param mock_get_tokens: Mocked function to get tokens for the user
        :type mock_get_tokens: unittest.mock.MagicMock

        :raises AssertationError: If any of the assertions fail
        :return: None
        """
        data = {
            'username': 'testuser',  # Missing password
        }
        response = self.client.post(self.url, data, format='json')
        
        print("Response content:", response.content)  

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Username/Email and password are required", json.loads(response.content).get('message'))

    @patch('onboarding.views.get_tokens_for_user')
    def test_user_not_found(self, mock_get_tokens):
        """Tests login with invaild username

        Sends a POST request with an invalid username and verifies:\n 
        - Response status code is Bad Request (400)\n 
        - Appropriate error message ("Invalid username or password.")

        :param mock_get_tokens: Mocked function to get tokens for the user
        :type mock_get_tokens: unittest.mock.MagicMock

        :raises AssertationError: If any of the assertions fail
        :return: None
        """
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
        """Tests login with multiple users

        Creates another user with the same email

        Sends a POST request with the same email and verifies:\n 
        - Response status code is Bad Request (400)\n 
        - Appropriate error message ("Multiple users found with given email.")

        :param mock_get_tokens: Mocked function to get tokens for the user
        :type mock_get_tokens: unittest.mock.MagicMock

        :raises AssertationError: If any of the assertions fail
        :return: None
        """
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
        """Tests login with an incorrect password

        Sends a POST request with an incorrect password and verifies:\n 
        - Response status code is Bad Request (400)\n 
        - Appropriate error message ("Invalid username or password.")

        :param mock_get_tokens: Mocked function to get tokens for the user
        :type mock_get_tokens: unittest.mock.MagicMock

        :raises AssertationError: If any of the assertions fail
        :return: None
        """
        data = {
            'username': 'testuser',
            'password': 'wrongpassword',  # Incorrect password
        }
        response = self.client.post(self.url, json.dumps(data), content_type='application/json')
        
        print("Response content:", response.content)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Invalid username or password.", json.loads(response.content).get('message'))

    def test_unverified_user(self):
        """Tests login with an unverified user

        Creates a new unverified user

        Sends a POST request with unverified username and verifies:\n 
        - Response status code is Bad Request (400)\n 
        - Appropriate error message ("User not verified.")

        :param mock_get_tokens: Mocked function to get tokens for the user
        :type mock_get_tokens: unittest.mock.MagicMock

        :raises AssertationError: If any of the assertions fail
        :return: None
        """
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
