from rest_framework import serializers
from django.contrib.auth.models import User
from onboarding.models import *

# defines serializers for models
class UserSerializer(serializers.ModelSerializer):
    """
    Serializes all fields of the built-in Django User model.
    """
    class Meta:
        model = User
        fields = '__all__'

class VerifiedUserSerializer(serializers.ModelSerializer):
    """
    Serializes all fields of the VerifiedUser model.
    """
    class Meta:
        model = VerifiedUser
        fields = '__all__'

class OTPSerializer(serializers.ModelSerializer):
    """
    Serializes all fields of the OTP (one-time password) model.
    """
    class Meta:
        model = OTP
        fields = '__all__'

class ExerciseSerializer(serializers.ModelSerializer):
    """
    Serializes all fields of the Exercise model.
    """
    class Meta:
        model = Exercise
        fields = '__all__'

class LoggedExerciseSerializer(serializers.ModelSerializer):
    """
    Serializes all fields of the LoggedExercise model.
    """
    class Meta:
        model = LoggedExercise
        fields = '__all__'

class RecommendedExerciseSerializer(serializers.ModelSerializer):
    """
    Serializes all fields of the RecommendedExercise model.
    """
    class Meta:
        model = RecommendedExercise
        fields = '__all__'


class ConsumableSerializer(serializers.ModelSerializer):
    """
    Serializes all fields of the Consumable model.
    """
    class Meta:
        model = Consumable
        fields = '__all__'

class LoggedConsumableSerializer(serializers.ModelSerializer):
    """
    Serializes all fields of the LoggedConsumable model.
    """
    class Meta:
        model = LoggedConsumable
        fields = '__all__'

class UserDataSerializer(serializers.ModelSerializer):
    """
    Serializes all fields of the UserData model.
    """
    class Meta:
        model = UserData
        fields = '__all__'

class RoutineExerciseSerializer(serializers.ModelSerializer):
    """
    Serializes the RoutineExercise model and includes the exercise's name.

    Additional Fields:
        exercise_name (str): Read-only field from the related Exercise model.
    """
    exercise_name = serializers.CharField(source='exercise.ex_name', read_only=True)

    class Meta:
        model = RoutineExercise
        fields = ['id','routine','exercise', 'exercise_name', 'order']


class RoutineSerializer(serializers.ModelSerializer):
    """
    Serializes the Routine model including related routine exercises.

    Additional Fields:
        routine_exercises (list): Read-only nested list of RoutineExerciseSerializer.
    """
    routine_exercises = RoutineExerciseSerializer(many=True, read_only=True)

    class Meta:
        model = Routine
        fields = ['id', 'user', 'name', 'description', 'created_at', 'routine_exercises']
        extra_kwargs = {'user': {'read_only': True}}

    def validate_name(self, value):
        """
        Returns a default name if none is provided.
        """
        if not value:
            return "My Routine"
        return value


class RoutineUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer used for updating a routine's name and description.
    """
    class Meta:
        model = Routine
        fields = ['name', 'description']

class LoggedRoutineSerializer(serializers.ModelSerializer):
    """
    Serializes the LoggedRoutine model with extra info like names.

    Additional Fields:
        routine_name (str): Read-only name of the related routine.
        user_name (str): Read-only username of the user who completed the routine.
    """
    routine_name = serializers.CharField(source='routine.name', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = LoggedRoutine
        fields = ['id', 'routine', 'user', 'completed_at', 'notes', 'duration', 'progress', 'routine_name', 'user_name']
        extra_kwargs = {'user': {'read_only': True}}

class UserMoodSerializer(serializers.ModelSerializer):
    """
    Serializes all fields of the UserMood model.
    """
    class Meta:
        model = UserMood
        fields = '__all__'