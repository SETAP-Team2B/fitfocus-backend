from rest_framework import serializers
from django.contrib.auth.models import User
from .models import *

# defines serializers for models
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class VerifiedUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = VerifiedUser
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

class RecommendedExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecommendedExercise
        fields = '__all__'


class ConsumableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consumable
        fields = '__all__'

class LoggedConsumableSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoggedConsumable
        fields = '__all__'