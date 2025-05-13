import json
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch
from django.contrib.auth.models import User 
from onboarding.models import OTP  
from datetime import timedelta
from django.utils import timezone

class ResetPasswordViewTests(APITestCase):
    """Test Case for the ResetPasswordView

    Contains tests for the password reset functionality, ensuring that the correct responses to the functions
    """
    def setUp(self):
        """Sets up the Test Case

        Is called before each test to initialize the URL for the reset password endpoint 
        
        Creates test user with an OTP instance marked as verified

        :return: None
        """
        self.url = reverse('reset-password')  
        self.user_email = 'test@example.com'
        self.user_password = 'OldPassword123!' 
        
        # Create a user instance
        self.user = User.objects.create_user(
            username='testuser',
            email=self.user_email,
            password=self.user_password
        )
        
        self.otp = OTP.objects.create(user=self.user, verified=True, expiry_time=timezone.now() + timedelta(minutes=5))

    @patch('onboarding.views.get_user_by_email_username')
    def test_reset_password_success(self, mock_get_user):
        """Tests successful password reset using a verified user
        
        Sends a POST request with new password and confirmation and verifies:\n
        - Response status code is OK (200)\n
        - Checks that the password has been updated in the database

        :param mock_get_user: Mocked function to get user by email or username
        :type mock_get_user: unittest.mock.MagicMock

        :raises AssertationError: If any of the assertions fail
        :return: None
        """
        mock_get_user.return_value = self.user 

        data = {
            'new_password': 'NewSecurePassword123!', 
            'confirm_password': 'NewSecurePassword123!'
        }
        response = self.client.post(self.url, data, format='json')
        print("Response content:", response.content)  
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Password Successfully Changed", json.loads(response.content).get('data'))
        
        # Check if the password has been updated
        self.user.refresh_from_db() 
        self.assertTrue(self.user.check_password('NewSecurePassword123!')) 

    @patch('onboarding.views.get_user_by_email_username')
    def test_otp_not_verified(self, mock_get_user):
        """Tests password reset with an unverified user

        Sets verifed status to false
        
        Sends a POST request with new password and confirmation and verifies\n
        - Response status code is Bad Request (400)\n
        - Appropriate error message ("OTP not verified. Validate or request another.")

        :param mock_get_user: Mocked function to get user by email or username
        :type mock_get_user: unittest.mock.MagicMock

        :raises AssertationError: If any of the assertions fail
        :return: None
        """
        mock_get_user.return_value = self.user  
        self.otp.verified = False  
        self.otp.save()

        data = {
            'new_password': 'NewSecurePassword123!',
            'confirm_password': 'NewSecurePassword123!'
        }
        response = self.client.post(self.url, data, format='json')
        print("Response content:", response.content) 
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("OTP not verified. Validate or request another.", json.loads(response.content).get('message'))

    @patch('onboarding.views.get_user_by_email_username')
    def test_setting_current_password(self, mock_get_user):
        """Tests password reset with same password as confirmation
        
        Sends a POST request with same password and confirmation and verifies\n
        - Response status code is Bad Request (400)\n
        - Appropriate error message ("Cannot set new password to current password.")

        :param mock_get_user: Mocked function to get user by email or username
        :type mock_get_user: unittest.mock.MagicMock

        :raises AssertationError: If any of the assertions fail
        :return: None
        """
        mock_get_user.return_value = self.user 

        data = {
            'new_password': self.user_password,  
            'confirm_password': self.user_password
        }
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        print("Response content:", response.content) 
        self.assertIn("Cannot set new password to current password.", json.loads(response.content).get('message'))

    @patch('onboarding.views.get_user_by_email_username')
    def test_weak_password(self, mock_get_user):
        """Tests password reset with weak new password
        
        Sends a POST request with weak new password and verifies:\n
        - Response status code is Bad Request (400)\n
        - Appropriate error message (New password is too weak.")

        :param mock_get_user: Mocked function to get user by email or username
        :type mock_get_user: unittest.mock.MagicMock

        :raises AssertationError: If any of the assertions fail
        :return: None
        """
        mock_get_user.return_value = self.user 

        data = {
            'new_password': '123', 
            'confirm_password': '123'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        print("Response content:", response.content) 
        self.assertIn("New password is too weak.", json.loads(response.content).get('message'))
