from django.db.utils import IntegrityError

from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from utils.api import api_error, api_success, check_input
from utils.exceptions import InvalidNameException, WeakPasswordError
from utils.validator import Messages, validate_email, \
    validate_username, check_password, check_name
from django.core import serializers
from django.contrib.auth import authenticate
import json

from django.contrib.auth.models import User
from .models import OTP
from .serializers import CreateUserSerializer, CreateOTPSerializer

from random import randint
import smtplib
from email.mime.multipart import MIMEMultipart  # for easy segregation of email sections
from email.mime.text import MIMEText
from datetime import timedelta
from django.utils import timezone
from .acct_type import AccountType


# Create your views here.
class CreateAccountView(generics.CreateAPIView):
    serializer_class = CreateUserSerializer

    def post(self, request, *args, **kwargs):
        if type(request.data) is not dict:
            return api_error("Invalid request type.")
        try:
            if validate_email(request.data['email']) \
                    and validate_username(request.data['username']):
                first_name = check_name(request.data['first_name'])
                last_name = check_name(request.data['last_name'])
                user = User.objects.create_user(email=request.data['email'],
                                                password=check_password(request.data['password']),
                                                username=request.data['username'])
                user.first_name = first_name
                user.last_name = last_name
                user.acct_type = AccountType.unverify
                user.save()

                return api_success({
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email,
                    "acct_type": user.acct_type
                })
            else:
                return api_error("Invalid email or username.")
        except IntegrityError:
            return api_error("Username already exists. Please try again.")
        except KeyError as keyErr:
            return api_error('{} is missing.'.format(keyErr.__str__()))
        except (WeakPasswordError, InvalidNameException, TypeError) as error:
            return api_error(error.__str__())


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),  # Refresh token (Used to get a new access token)
        'access': str(refresh.access_token),  # Main token used for authentication
    }

# given a request with an email/password, finds the user associated with the account
# used multiple times by several functions
# should either return a User object or call an api_error.
def get_user_by_email_username(request):
    target_user: User | None = None

    # following if/elif/else statements find the user based on the inputted email/username
    if "email" in request.data:
        try:
            target_user = User.objects.get(email=request.data["email"])
        except User.DoesNotExist:
            return api_error("Could not find associated user.")
    elif "username" in request.data:        
        try:
            target_user = User.objects.get(username=request.data["username"])
        except User.DoesNotExist:
            return api_error("Could not find associated user.")
    else:
        return api_error("No email or username was provided.")
    
    return target_user


class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return api_error("Username and password are required.")

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
        return api_error("Invalid username or password.")


class GenerateOTPView(generics.CreateAPIView):
    serializer_class = CreateOTPSerializer

    # function which uses the OTP model

    # input should be:
    # - valid username/email
    # - a custom OTP (optional, probably never useful)

    # output should be (no actual values are necessary to be returned, only for debug purposes):
    # - SUCCESS if the following conditions are met:
    # ----- there exists a user with the inputted username and/or email address
    # ----- the email is succesfully sent
    # - FAIL if any of the above conditions are not met
    def post(self, request, custom_otp: str = None, *args, **kwargs):
        target_user: User | None = get_user_by_email_username(request)

        # generates OTP and send to user, contains 6 digits from 0-9
        otp = (f"{randint(0, 999999):06d}" if custom_otp == None else custom_otp)

        try:
            # REMOVE FROM GITHUB IF POSSIBLE
            SENDER_EMAIL = 'fitfocus.noreply@gmail.com'  # The email you setup to send the email using app password
            SENDER_EMAIL_APP_PASSWORD = 'akuymdiidbdgempt'  # The app password you generated

            # Construct SMTP server
            smtpserver = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            smtpserver.ehlo()
            smtpserver.login(SENDER_EMAIL, SENDER_EMAIL_APP_PASSWORD)

            # Create email contents
            # NOTE: for new lines, use <br> as the email formatter is done via HTML.
            message = MIMEMultipart()
            message["To"] = target_user.email
            message["From"] = SENDER_EMAIL
            message["Subject"] = "Your FitFocus One-Time Password"
            messageText = MIMEText(
                f"Your FitFocus OTP is {otp}.<br>This OTP will expire within 5 minutes.<br>Should you require a new OTP, request another one.",
                "html")
            message.attach(messageText)

            notes_text = "Email successfully sent. Don\'t see it? Be sure to check spam folders."

            # Send the email and close the server
            smtpserver.sendmail(
                from_addr=SENDER_EMAIL,
                to_addrs=target_user.email,
                msg=message.as_string()
            )
            smtpserver.close()

            # create/update the existing OTP in the OTP table
            # created_at and expiry_time SHOULD automatically update
            # new_otp does not set itself exactly equal to 5 mins past created at,
            # so it must be manually set after creating the object

            new_otp: OTP | None = None
            try:
                new_otp = OTP.objects.get(user=target_user)
            except OTP.DoesNotExist:
                new_otp = OTP.objects.create(user=target_user)
            except OTP.MultipleObjectsReturned:
                # if there are somehow multiple instances of an OTP for a specific user
                # simplest option is to cull all existing entries and create a new one
                OTP.objects.get(user=target_user).delete()
                new_otp = OTP.objects.create(user=target_user)

            new_otp.otp = otp
            new_otp.created_at = timezone.now()
            new_otp.expiry_time = new_otp.created_at + timezone.timedelta(minutes=5)
            new_otp.verified = False

            # MAKE SURE TO SAVE WHEN UPDATING. 15 minutes of bugfixing to find out objects dont save without this lol
            new_otp.save()

            # returns all the data from the OTP.
            # "user" displays the username as User objects will not be displayed in a JSON format for security reasons, 
            return api_success("OTP sent.")
        except smtplib.SMTPException:
            return api_error("Email failed to send.")


class ValidateOTPView(generics.CreateAPIView):
    serializer_class = CreateOTPSerializer

    # post should include:
    # - username/email to the account
    # - attempted OTP (6 digits from 0-9)

    # api call should return a single response:
    # - "success" if all of the conditions are met:
    # ----- there is a user with the correct username and/or email address
    # ----- attempt datetime <= OTP expiry_time
    # ----- attempted OTP = stored OTP
    # - "fail" OR an error description if any of the above conditions are not met
    def post(self, request, *args, **kwargs):
        target_user: User | None = get_user_by_email_username(request)

        # determines if an OTP was included
        if "otp" not in request.data:
            return api_error("No OTP was provided.")

        # gathers the OTP data for the user
        stored_otp = OTP.objects.get(user=target_user)

        # checks if the OTP has passed expiry
        if timezone.now() > stored_otp.expiry_time:
            return api_error(f"The OTP has expired. Please request a new OTP.")

        if request.data["otp"].strip() == stored_otp.otp:
            # checks if the OTP has already been entered before
            if stored_otp.verified: return api_error("This OTP has already been entered before.")

            stored_otp.verified = True
            stored_otp.save()
            return api_success("success")
        else:
            return api_error("The OTP you entered is incorrect.")
        
class ResetPasswordView(generics.CreateAPIView):
    serializer_class = CreateUserSerializer

    def post(self, request, *args, **kwargs):
        target_user: User | None = get_user_by_email_username(request)

        # checks if the user has verified their OTP before continuing
        if not (OTP.objects.get(user=target_user).verified):
            return api_error("OTP not verified. Validate or request another.")
                       
        new_password = ""
        confirm_password = ""
        
        if 'new_password' in request.data:
            new_password = request.data['new_password']
        else:
            return api_error("No password entered.")
        
        if 'confirm_password' in request.data:
            confirm_password = request.data['confirm_password']
        else:
            return api_error("No password confirmation entered.")

        if new_password != confirm_password:
            return api_error("Passwords do not match.")
        
        if new_password == target_user.password:
            return api_error("Cannot set new password to current password.")
        
        try:
            target_user.password = check_password(new_password)
            target_user.save()

            # sets the current OTP to become invalid, otherwise this would make the user able to change their password an unlimited amount of times through the API
            # while not possible in the app as changing the password redirects the user to the login/home screen
            # very rare scenario but good for security
            currentOTP: OTP = OTP.objects.get(user=target_user)
            currentOTP.verified = False
            currentOTP.save()

            return api_success("Password Successfully Changed")
        except WeakPasswordError:
            return api_error("New password is too weak.")