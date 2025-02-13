from rest_framework import generics, permissions
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from utils.api import api_error, api_success, check_input
from utils.strings import Messages
from .user_serializers import CreateUserSerializer
from django.core import serializers
from django.contrib.auth import authenticate
import json


# Create your views here.
class CreateAccountView(generics.CreateAPIView):
    serializer_class = CreateUserSerializer

    def post(self, request, *args, **kwargs):
        try:
            first_name = request.data['first_name']
            last_name = request.data['last_name']
            user = User.objects.create_user(email=request.data['email'],
                                            password=request.data['password'],
                                            username=request.data['username'])
            user.first_name = first_name
            user.last_name = last_name
            user.save()

            # assuming obj is a model instance

            return api_success({
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email
            })
        except KeyError as keyErr:
            return api_error('{} is missing'.format(keyErr.__str__()))

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),  # Refresh token (Used to get a new access token)
        'access': str(refresh.access_token),  # Main token used for authentication
    }

class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return api_error("Username and password are required")

        user = authenticate(username=username, password=password)
        if user:
            tokens = get_tokens_for_user(user)  # Generate JWT tokens
            return api_success({
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "token": tokens['access'],  # Return access token for authentication
                "refresh_token": tokens['refresh'],  # Refresh token for re-authentication
            })
        return api_error("Invalid username or password")