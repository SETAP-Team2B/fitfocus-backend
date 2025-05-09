import json
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch
from django.contrib.auth.models import User
from onboarding.models import Exercise, LoggedExercise  

class LogExerciseViewTests(APITestCase):
    """Test Case for the LogExerciseView

    Contains test for logging user exercise functionality, ensuing correct responses to functions
    """
    def setUp(self):
        """Sets up the Test Case

        Is called before each test to initialise the URL for the log exercise end point

        Creates a test User and test Exercise to use in test
        """
        self.url = reverse('log-exercise') 
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='password123')
        self.exercise = Exercise.objects.create(ex_name='Push Up', ex_type='Muscle', ex_body_area='Chest', equipment_needed='None')

    @patch('onboarding.views.get_user_by_email_username')
    @patch('onboarding.views.get_exercise_by_name')
    def test_log_exercise_success(self, mock_get_exercise, mock_get_user):
        """Tests the successful logging of an exercise

        Sends POST request with valid exercise data and verifies:\n
        - Response status code is OK (200)\n
        - LoggedExercise instance was created with matching data\n
        - Response message indicating success ("Exercised Logged!")

        :param mock_get_exercise: Mocked function to get exercise by name.
        :type mock_get_exercise: unittest.mock.MagicMock
        :param mock_get_user: Mocked function to get user by email or username
        :type mock_get_user: unittest.mock.MagicMock

        :raises AssertationError: If any of the assertions fail
        :return: None
        """
        mock_get_user.return_value = self.user
        mock_get_exercise.return_value = self.exercise

        data = {
            'date_logged': '2023-10-01',
            'sets': 3,
            'reps': 10,
            'distance': None,
            'duration': None,
            'equipment_weight': 50,
            'equipment_weight_units': 'kg'
        }
        response = self.client.post(self.url, data, format='json')

        print("Response content:", response.content)  

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Exercised Logged!", json.loads(response.content).get('data'))

        # Check if the LoggedExercise instance was created
        logged_exercise = LoggedExercise.objects.first()
        self.assertIsNotNone(logged_exercise)
        self.assertEqual(logged_exercise.user, self.user)
        self.assertEqual(logged_exercise.exercise, self.exercise)
        self.assertEqual(logged_exercise.sets, 3)
        self.assertEqual(logged_exercise.reps, 10)

    def test_user_not_found(self):
        """Tests the logging of an exercise when the user is not found

        Sends POST request with non existent username and verifies:\n
        - Response status code is Bad Request (400)\n
        - Appropriate error message ("Could not find associated user.")
        """
        data = {
            'username': 'nonexistentuser',  # Use a username that does not exist
            'date_logged': '2023-10-01',
            'sets': 3,
            'reps': 10,
            'exercise_name': 'Push Up' 
        }
        response = self.client.post(self.url, data, format='json')

        print("Response content:", response.content) 
        print("Response status code:", response.status_code)  

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)  
        self.assertIn("Could not find associated user.", json.loads(response.content).get('message'))

    @patch('onboarding.views.get_user_by_email_username')
    @patch('onboarding.views.get_exercise_by_name')
    def test_no_exercise_info(self, mock_get_exercise, mock_get_user):
        """Tests the logging of an exercise with missing data

        Sends POST request with missing exercise data and verifies:\n
        - Response status code is Bad Request (400)\n
        - Appropriate error message ("Exercise log must contain some exercise information.")

        :param mock_get_exercise: Mocked function to get exercise by name.
        :type mock_get_exercise: unittest.mock.MagicMock
        :param mock_get_user: Mocked function to get user by email or username
        :type mock_get_user: unittest.mock.MagicMock

        :raises AssertationError: If any of the assertions fail
        :return: None
        """
        mock_get_user.return_value = self.user  
        mock_get_exercise.return_value = self.exercise  

        data = {
            'date_logged': '2023-10-01',
            # No other exercise information provided
        }
        response = self.client.post(self.url, data, format='json')

        print("Response content:", response.content)  
        print("Response status code:", response.status_code) 

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Exercise log must contain some exercise information.", json.loads(response.content).get('message'))
