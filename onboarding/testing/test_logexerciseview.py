import json
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch
from django.contrib.auth.models import User
from onboarding.models import Exercise, LoggedExercise  

class LogExerciseViewTests(APITestCase):
    def setUp(self):
        self.url = reverse('log-exercise')  # Adjust the URL name based on your URL configuration
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='password123')
        self.exercise = Exercise.objects.create(ex_name='Push Up', ex_type='Muscle', ex_body_area='Chest', equipment_needed='None')

    @patch('onboarding.views.get_user_by_email_username')
    @patch('onboarding.views.get_exercise_by_name')
    def test_log_exercise_success(self, mock_get_exercise, mock_get_user):
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

        print("Response content:", response.content)  # Debugging output

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
        data = {
            'username': 'nonexistentuser',  # Use a username that does not exist
            'date_logged': '2023-10-01',
            'sets': 3,
            'reps': 10,
            'exercise_name': 'Push Up' 
        }
        response = self.client.post(self.url, data, format='json')

        # Print the response content for debugging
        print("Response content:", response.content) 
        print("Response status code:", response.status_code)  

        # Expecting 404 Not Found for user not found
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)  
        self.assertIn("Could not find associated user.", json.loads(response.content).get('message'))

    @patch('onboarding.views.get_user_by_email_username')
    @patch('onboarding.views.get_exercise_by_name')
    def test_missing_date(self, mock_get_exercise, mock_get_user):
        mock_get_user.return_value = self.user
        mock_get_exercise.return_value = self.exercise 

        data = {
            # 'date_logged' is intentionally left out to test the missing date scenario
            'sets': 3,
            'reps': 10,
        }
        response = self.client.post(self.url, data, format='json')

        # Print the response content for debugging
        print("Response content:", response.content)
        print("Response status code:", response.status_code) 

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)  
        self.assertIn("A date for the exercise log must be provided.", json.loads(response.content).get('message'))

    @patch('onboarding.views.get_user_by_email_username')
    @patch('onboarding.views.get_exercise_by_name')
    def test_no_exercise_info(self, mock_get_exercise, mock_get_user):
        mock_get_user.return_value = self.user  
        mock_get_exercise.return_value = self.exercise  

        data = {
            'date_logged': '2023-10-01',
            # No exercise information provided
        }
        response = self.client.post(self.url, data, format='json')

        # Print the response content for debugging
        print("Response content:", response.content)  
        print("Response status code:", response.status_code) 

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Exercise log must contain some exercise information.", json.loads(response.content).get('message'))
