from django.db.utils import IntegrityError

from rest_framework import generics, permissions
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from utils.api import api_error, api_success, check_input
from utils.exceptions import InvalidNameException, WeakPasswordError
from utils.validator import Messages, validate_email, \
    validate_username, check_password, check_name
from .user_serializers import CreateUserSerializer
from django.core import serializers
from django.contrib.auth import authenticate
import json


# Create your views here.
class CreateAccountView(generics.CreateAPIView):
    serializer_class = CreateUserSerializer

    def post(self, request, *args, **kwargs):
        if validate_email(request.data['email']) \
                and validate_username(request.data['username']):
            try:
                first_name = check_name(request.data['first_name'])
                last_name = check_name(request.data['last_name'])
                user = User.objects.create_user(email=request.data['email'],
                                                password=check_password(request.data['password']),
                                                username=request.data['username'])
                user.first_name = first_name
                user.last_name = last_name
                user.save()

                return api_success({
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email
                })
            except IntegrityError:
                return api_error("Username already exist. Please try again")
            except KeyError as keyErr:
                return api_error('{} is missing'.format(keyErr.__str__()))
            except (WeakPasswordError, InvalidNameException) as error:
                return api_error(error.__str__())
        else:
            return api_error("Invalid email or username")


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
