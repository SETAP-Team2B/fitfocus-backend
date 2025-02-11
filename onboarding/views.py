from rest_framework import generics, permissions
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.views import APIView

from utils.api import api_error, api_success, check_input
from utils.strings import Messages
from .user_serializers import CreateUserSerializer
from django.core import serializers
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
