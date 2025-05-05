import json
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from onboarding.models import Exercise 

class ExerciseViewTests(APITestCase):
    def setUp(self):
        self.url = reverse('create-exercise')

    def test_create_exercise_success(self):
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

        self.assertEqual(response.status_code, status.HTTP_200_OK)  # Change to expect 200 OK

        response_data = json.loads(response.content)

        self.assertEqual(response_data['data']['ex_name'], data['ex_name'])
        self.assertEqual(response_data['data']['ex_type'], data['ex_type'])
        self.assertEqual(response_data['data']['ex_body_area'], data['ex_body_area'])

    def test_missing_required_fields(self):
        data = {
            'ex_name': 'Push Up',  # Missing other required fields
        }
        response = self.client.post(self.url, data, format='json')
        
        print("Response content:", response.content)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Necessary Field(s) are empty", json.loads(response.content).get('message'))

    def test_invalid_muscle_type(self):
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
        self.assertIn("Inavlid Muscle Type", json.loads(response.content).get('message'))

    def test_invalid_exercise_type(self):
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
        self.assertIn("Inavlid Body Area Type", json.loads(response.content).get('message'))

