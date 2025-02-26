from rest_framework import serializers
from django.contrib.auth.models import User
from .models import OTP
from .models import Exercise

class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class CreateOTPSerializer(serializers.ModelSerializer):
    class Meta:
        model = OTP
        fields = '__all__'

class CreateExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = '__all__'

class GetExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model=Exercise
        fields = (
            'ex_name',
            'ex_type',
            'ex_body_area',
            'equipment_needed',
            'ex_target_muscle'
        )