from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch
from .models import LoggedExercise, User, Exercise  # Adjust based on your project structure

class LogExerciseViewTest(APITestCase):
    def setUp(self):
        # Create a user and an exercise for testing
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='password')
        self.exercise = Exercise.objects.create(ex_name='Running')  # Adjust based on your Exercise model
        self.url = reverse('log-exercise')  # Replace with the actual URL name for your view

    @patch('your_app.views.get_user_by_email_username')  # Adjust the import path
    @patch('your_app.views.get_exercise_by_name')  # Adjust the import path
    def test_post_valid_data(self, mock_get_exercise, mock_get_user):
        # Mock the return values for the user and exercise retrieval
        mock_get_user.return_value = self.user
        mock_get_exercise.return_value = self.exercise

        # Prepare a valid request
        request_data = {
            'date_logged': '2023-10-01',
            'time_logged': '10:00',
            'sets': 3,
            'reps': 10,
            'distance': 5,
            'distance_units': 'km',
            'duration': 30,
            'equipment_weight': 50,
            'equipment_weight_units': 'kg'
        }

        # Make the POST request
        response = self.client.post(self.url, data=request_data)

        # Check that the response is successful
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], "Exercised Logged!")

        # Check that the LoggedExercise instance was created
        self.assertTrue(LoggedExercise.objects.filter(user=self.user, date_logged='2023-10-01').exists())

    @patch('your_app.views.get_user_by_email_username')
    @patch('your_app.views.get_exercise_by_name')
    def test_post_missing_date(self, mock_get_exercise, mock_get_user):
        mock_get_user.return_value = self.user
        mock_get_exercise.return_value = self.exercise

        # Prepare a request with missing date_logged
        request_data = {
            'time_logged': '10:00',
            'sets': 3,
            'reps': 10
        }

        # Make the POST request
        response = self.client.post(self.url, data=request_data)

        # Check that the response indicates an error
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], "A date for the exercise log must be provided.")

    @patch('your_app.views.get_user_by_email_username')
    @patch('your_app.views.get_exercise_by_name')
    def test_post_no_exercise_info(self, mock_get_exercise, mock_get_user):
        mock_get_user.return_value = self.user
        mock_get_exercise.return_value = self.exercise

        # Prepare a request with no exercise information
        request_data = {
            'date_logged': '2023-10-01'
        }

        # Make the POST request
        response = self.client.post(self.url, data=request_data)

        # Check that the response indicates an error
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], "Exercise log must contain some exercise information.")

    @patch('your_app.views.get_user_by_email_username')
    @patch('your_app.views.get_exercise_by_name')
    def test_get_exercise_logs(self, mock_get_exercise, mock_get_user):
        mock_get_user.return_value = self.user
        mock_get_exercise.return_value = self.exercise

        # Create a LoggedExercise instance for testing
        LoggedExercise.objects.create(
            user=self.user,
            exercise=self.exercise,
            date_logged='2023-10-01',
            time_logged='10:00'
        )
