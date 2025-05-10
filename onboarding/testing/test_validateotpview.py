import json
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch
from django.contrib.auth.models import User
from onboarding.models import OTP, VerifiedUser 
from django.utils import timezone
from datetime import timedelta

class ValidateOTPViewTests(APITestCase):
    """Test Case for the ValidateOTPView

    Contains tests for the OTP validation functionality, ensuring that the correct responses to the functions
    """
    def setUp(self):
        """Sets up the Test Case

        Is called before each test to initialize the URL for the validate otp endpoint 
        
        Creates test user with an OTP instance marked as unverified

        :return: None
        """
        self.url = reverse('validate-otp') 
        self.user_email = 'test@example.com'
        self.user_password = 'OldPassword123!'  
        
        #Create a user instance
        self.user = User.objects.create_user(
            username='testuser',
            email=self.user_email,
            password=self.user_password
        )

        #Create an OTP instance for the user
        self.otp = OTP.objects.create(
            user=self.user,
            otp='123456',
            created_at=timezone.now(),
            expiry_time=timezone.now() + timedelta(minutes=5),
            verified=False
        )

    @patch('onboarding.views.get_user_by_email_username')
    def test_validate_otp_success(self, mock_get_user):
        """Tests successful OTP validation
        
        Sends a POST request with valid otp and verifies:\n
        - Response status code is OK (200)\n
        - Message indicating success ("success")

        :param mock_get_user: Mocked function to get user by email or username
        :type mock_get_user: unittest.mock.MagicMock

        :raises AssertationError: If any of the assertions fail or the response content is not valid JSON
        :return: None
        """
        mock_get_user.return_value = self.user 

        data = {
            'otp': '123456',
        }
        response = self.client.post(self.url, json.dumps(data), content_type='application/json')
        
        print("Response content:", response.content) 

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        #Ensure the response content is valid JSON
        try:
            response_data = json.loads(response.content)
        except json.JSONDecodeError:
            self.fail("Response content is not valid JSON")

        self.assertIn("success", json.loads(response.content).get('data'))

    @patch('onboarding.views.get_user_by_email_username')
    def test_otp_expired(self, mock_get_user):
        """Tests OTP validation attempt with expried OTP

        Sets OTP to be expired
        
        Sends a POST request with expired otp and verifies:\n
        - Response status code is Bad Request (400)\n
        - Appropriate error message ("The OTP has expired. Please request a new OTP.")

        :param mock_get_user: Mocked function to get user by email or username
        :type mock_get_user: unittest.mock.MagicMock

        :raises AssertationError: If any of the assertions fail
        :return: None
        """
        mock_get_user.return_value = self.user

        # Set the OTP to be expired
        self.otp.expiry_time = timezone.now() - timedelta(minutes=1)
        self.otp.save()

        data = {
            'otp': '123456',
        }
        response = self.client.post(self.url, data, format='json')
        
        print("Response content:", response.content)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("The OTP has expired. Please request a new OTP.", json.loads(response.content).get('message'))

    @patch('onboarding.views.get_user_by_email_username')
    def test_incorrect_otp(self, mock_get_user):
        """Tests OTP validation attempt with incorrect OTP

        Sets OTP to be expired
        
        Sends a POST request with expired otp and verifies:\n
        - Response status code is Bad Request (400)\n
        - Appropriate error message ("The OTP has expired. Please request a new OTP.")

        :param mock_get_user: Mocked function to get user by email or username
        :type mock_get_user: unittest.mock.MagicMock

        :raises AssertationError: If any of the assertions fail
        :return: None
        """
        mock_get_user.return_value = self.user 

        data = {
            'otp': '654321',  # Incorrect OTP
        }
        response = self.client.post(self.url, data, format='json')
        
        print("Response content:", response.content)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("The OTP you entered is incorrect.", json.loads(response.content).get('message'))

    @patch('onboarding.views.get_user_by_email_username')
    def test_otp_already_verified(self, mock_get_user):
        """Tests OTP validation attempt with already verified OTP

        Sets OTP to be verified
        
        Sends a POST request with verified otp and verifies:\n
        - Response status code is Bad Request (400)\n
        - Appropriate error message ("This OTP has already been entered before.")

        :param mock_get_user: Mocked function to get user by email or username
        :type mock_get_user: unittest.mock.MagicMock

        :raises AssertationError: If any of the assertions fail
        :return: None
        """
        mock_get_user.return_value = self.user

        # Mark the OTP as verified
        self.otp.verified = True
        self.otp.save()

        data = {
            'otp': '123456',
        }
        response = self.client.post(self.url, data, format='json')
        
        print("Response content:", response.content)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("This OTP has already been entered before.", json.loads(response.content).get('message'))

    @patch('onboarding.views.get_user_by_email_username')
    def test_no_otp_provided(self, mock_get_user):
        """Tests OTP validation attempt with no OTP
        
        Sends a POST request with no otp and verifies:\n
        - Response status code is Bad Request (400)\n
        - Appropriate error message ("No OTP was provided.")

        :param mock_get_user: Mocked function to get user by email or username
        :type mock_get_user: unittest.mock.MagicMock

        :raises AssertationError: If any of the assertions fail
        :return: None
        """
        mock_get_user.return_value = self.user

        data = {}  # No OTP provided
        response = self.client.post(self.url, data, format='json')
        
        print("Response content:", response.content)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("No OTP was provided.", json.loads(response.content).get('message'))
