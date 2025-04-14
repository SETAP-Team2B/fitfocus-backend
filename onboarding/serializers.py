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

class UserDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserData
        fields = '__all__'

class RoutineExerciseSerializer(serializers.ModelSerializer):
    exercise_name = serializers.CharField(source='exercise.ex_name', read_only=True)

    class Meta:
        model = RoutineExercise
        fields = ['id','routine','exercise', 'exercise_name', 'order']


class RoutineSerializer(serializers.ModelSerializer):
    routine_exercises = RoutineExerciseSerializer(many=True, read_only=True)

    class Meta:
        model = Routine
        fields = ['id', 'user', 'name', 'description', 'created_at', 'routine_exercises']
        extra_kwargs = {'user': {'read_only': True}}

    def validate_name(self, value):
        # If no name is provided, return "My Routine"
        if not value:
            return "My Routine"
        return value


# Serializer for updating routines
class RoutineUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Routine
        fields = ['name', 'description']


class UserMoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserMood
        fields = '__all__'