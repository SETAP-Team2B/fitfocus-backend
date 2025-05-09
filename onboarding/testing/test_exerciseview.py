import json
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from onboarding.models import Exercise 

class ExerciseViewTests(APITestCase):
    """The Test Case for the ExerciseView

    Contains tests for exercise creation functionality, ensuring correct responses to functions
    """
    def setUp(self):
        self.url = reverse('create-exercise')
        """Sets up the Test Case

        Is called before each test to initialise the URL for the exercise creation end point

        :return: None
        """

    def test_create_exercise_success(self):
        """Test the successful creation of an exercise

        Sends POST request with valid exercise data and verifies:\n
        - Response status code is OK (200)\n
        - the response contains correct exercise data\n
        - The exercise data matches the input data

        :raises AssertationError: If any of the assertions fail
        :return: None
        """
        data = {
            'ex_name': 'Push Up',
            'ex_type': 'Muscle',
            'ex_body_area': 'Chest',
            'equipment_needed': 'None',
            'ex_target_muscle': 'Pectorals',
            'ex_secondary_muscle_1': 'Triceps',
            'ex_secondary_muscle_2': 'Deltoids'
        }
        response = self.client.post(self.url, data, format='json')

        print("Response content:", response.content) 
        print("Response status code:", response.status_code)

        self.assertEqual(response.status_code, status.HTTP_200_OK) 
        response_data = json.loads(response.content)

        self.assertEqual(response_data['data']['ex_name'], data['ex_name'])
        self.assertEqual(response_data['data']['ex_type'], data['ex_type'])
        self.assertEqual(response_data['data']['ex_body_area'], data['ex_body_area'])

    def test_missing_required_fields(self):
        """Tests exercise creation with missing fields

        Sends POST request with missing fields and verifies:\n
        - Bad request (400)\n
        - Appropriate error message ("Necessary Field(s) are empty")

        :raises AssertationError: If any of the assertions fail
        :return: None
        """
        data = {
            'ex_name': 'Push Up',  # Missing other required fields
        }
        response = self.client.post(self.url, data, format='json')
        
        print("Response content:", response.content)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Necessary Field(s) are empty", json.loads(response.content).get('message'))

    def test_invalid_muscle_type(self):
        """Tests exercise creation with invalid muscle type

        Sends POST request with invalid muscle type and verifies:\n
        - Bad request (400)\n
        - Appropriate error message ("Invalid Muscle Type")

        :raises AssertationError: If any of the assertions fail
        :return: None
        """
        data = {
            'ex_name': 'Push Up',
            'ex_type': 'Muscle',
            'ex_body_area': 'Chest',
            'equipment_needed': 'None',
            'ex_target_muscle': 'InvalidMuscle',  # Invalid muscle type
            'ex_secondary_muscle_1': 'Triceps',
            'ex_secondary_muscle_2': 'Deltoids'
        }
        response = self.client.post(self.url, data, format='json')
        
        print("Response content:", response.content)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Invalid Muscle Type", json.loads(response.content).get('message'))

    def test_invalid_exercise_type(self):
        """Tests exercise creation with invalid exercise type

        Sends POST request with invalid exercise type and verifies:\n
        - Bad request (400)\n
        - Appropriate error message ("Invalid Exercise Type")

        :raises AssertationError: If any of the assertions fail
        :return: None
        """
        data = {
            'ex_name': 'Push Up',
            'ex_type': 'InvalidType',  # Invalid exercise type
            'ex_body_area': 'Chest',
            'equipment_needed': 'None',
            'ex_target_muscle': 'Pectorals',
            'ex_secondary_muscle_1': 'Triceps',
            'ex_secondary_muscle_2': 'Deltoids'
        }
        response = self.client.post(self.url, data, format='json')
        
        print("Response content:", response.content)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Invalid Exercise Type", json.loads(response.content).get('message'))

    def test_invalid_body_area_type(self):
        """Tests exercise creation with invalid body area type

        Sends POST request with invalid body area type and verifies:\n
        - Bad request (400)\n
        - Appropriate error message ("Invalid Body Area Type")

        :raises AssertationError: If any of the assertions fail
        :return: None
        """
        data = {
            'ex_name': 'Push Up',
            'ex_type': 'Muscle',
            'ex_body_area': 'InvalidArea',  # Invalid body area type
            'equipment_needed': 'None',
            'ex_target_muscle': 'Pectorals',
            'ex_secondary_muscle_1': 'Triceps',
            'ex_secondary_muscle_2': 'Deltoids'
        }
        response = self.client.post(self.url, data, format='json')
        
        print("Response content:", response.content)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Invalid Body Area Type", json.loads(response.content).get('message'))

