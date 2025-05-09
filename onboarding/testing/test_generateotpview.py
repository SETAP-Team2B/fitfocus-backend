import json
import smtplib
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch
from django.contrib.auth.models import User
from onboarding.views import GenerateOTPView 
from onboarding.models import OTP

class GenerateOTPViewTests(APITestCase):
    """The Test Case for the GenerateOTPView

    Contains tests for generating and sending an OTP to user email, ensuing correct responses to functions
    """
    def setUp(self):
        """Sets up the Test Case

        Is called before each test to initialise the URL for the generate otp end point

        Creates a test User to use to simulate sending otp email

        :return: None
        """
        self.url = reverse('generate-otp')
        self.user_email = 'test@example.com'
        self.user_password = 'OldPassword123!' 
        
        self.user = User.objects.create_user(
            username='testuser',
            email=self.user_email,
            password=self.user_password
        )

    @patch('onboarding.views.smtplib.SMTP_SSL')
    def test_generate_otp_success(self, mock_smtp):
        """Tests the successful generation and sending of OTP

        Sends POST request to simulate generation and email sending proccess and verifies:\n
        - Response status code is OK (200)\n
        - Response message indicating success ("OTP sent.")

        :param mock_smtp: Mocked SMTP_SSL object to simulate email sending
        :type mock_smtp: unittest.mock.MagicMock

        :raises AssertationError: If any of the assertions fail or response content is not valid JSON
        :return: None
        """
        # Mock the SMTP server to simulate sending an email
        mock_smtp.return_value.__enter__.return_value.sendmail = lambda *args, **kwargs: None
        
        data = {
            'username': 'testuser',  # or 'email': self.user_email
        }
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        try:
            response_data = json.loads(response.content)
        except json.JSONDecodeError:
            self.fail("Response content is not valid JSON")

        print("Response content:", response.content)

        self.assertIn("OTP sent.", json.loads(response.content).get('data'))

    @patch('onboarding.views.smtplib.SMTP_SSL')
    def test_email_sending_failure(self, mock_smtp):
        """Tests the faliure of a generation and sending of OTP

        Sends POST request to simulate faluire in email sending proccess by raising SMTPException and verifies:\n
        - Response status code is Bad Request (400)\n
        - Appropriate error message ("Email failed to send.")

        :param mock_smtp: Mocked SMTP_SSL object to simulate email sending
        :type mock_smtp: unittest.mock.MagicMock

        :raises AssertationError: If any of the assertions fail
        :return: None
        """
        # Simulate an SMTP exception
        mock_smtp.side_effect = smtplib.SMTPException
        
        data = {
            'username': 'testuser',
        }
        response = self.client.post(self.url, data, format='json')
        
        print("Response content:", response.content)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Email failed to send.", json.loads(response.content).get('message'))
