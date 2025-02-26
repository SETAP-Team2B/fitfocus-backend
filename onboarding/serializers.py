from rest_framework import serializers
from django.contrib.auth.models import User
from .models import OTP, Exercise, LoggedExercise

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class OTPSerializer(serializers.ModelSerializer):
    class Meta:
        model = OTP
        fields = '__all__'

class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = '__all__'

class LoggedExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoggedExercise
        fields = '__all__'