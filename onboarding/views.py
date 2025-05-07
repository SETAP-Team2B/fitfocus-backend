from django.db.utils import IntegrityError

from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.http import Http404
from django.db.models import F
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from rest_framework.generics import RetrieveAPIView
from utils.api import api_error, api_success
from utils.exceptions import InvalidNameException, WeakPasswordError
from utils.validator import validate_email, \
    validate_username, check_password, check_name
from django.contrib.auth import authenticate

from django.contrib.auth.models import User
from onboarding.models import *
from onboarding.serializers import *

from random import randint
import smtplib
from email.mime.multipart import MIMEMultipart  # for easy segregation of email sections
from email.mime.text import MIMEText
from datetime import timedelta
from django.utils import timezone
from django.http import JsonResponse
import json
import csv

# for exercise recommendation
import random
from django.db.models import Avg
from math import floor
import numpy as np
import pandas as pd
from sklearn.neighbors import KNeighborsClassifier
from django.forms.models import model_to_dict
from statistics import median_low

import datetime


# ensures all required attributes are in the request
# reusable to all get/post functions

def check_all_required_keys_present(request, keys: list):
    if type(request) != dict:
        return api_error("Request was not a dictionary.")

    # if the key is not present in request.data OR is an empty string where a string should be, raise an api error
    for key in keys:
        if key not in list(request.data.keys()):
            return api_error(f"Request must contain (at least) the following: {', '.join(keys)}")
        else:
            if request.data[key] == "" or request.data[key] == None:
                return api_error(f"{key} was found, but is empty.")

    return


# generates and returns token for user
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),  # Refresh token (Used to get a new access token)
        'access': str(refresh.access_token),  # Main token used for authentication
    }


# given a request with an email/password, finds the user associated with the account
# used multiple times by several functions
# should either return a User object or call an api_error.
# ALSO LOOKS THROUGH QUERY PARAMS AS THAT IS THE ONLY WAY TO HANDLE IT IN DART
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
    elif "email" in request.query_params:
        try:
            target_user = User.objects.get(email=request.query_params["email"])
        except User.DoesNotExist:
            return api_error("Could not find associated user.")
    elif "username" in request.query_params:        
        try:
            target_user = User.objects.get(username=request.query_params["username"])
        except User.DoesNotExist:
            return api_error("Could not find associated user.")
    else:
        return api_error("No email or username was provided.")
    
    return target_user

def get_exercise_by_name(request):
    target_exercise: Exercise | None = None

    # looks for an exercise with the given name within the database
    if "ex_name" in request.data:
        try:
            target_exercise = Exercise.objects.get(ex_name=request.data["ex_name"])
        except Exercise.DoesNotExist:
            return api_error("Could not find exercise with given name.")
        except Exercise.MultipleObjectsReturned:
            return api_error("Multiple exercises found.")
    else:
        return api_error("No exercise name found.")
    
    return target_exercise

def recommend_exercises(user: User, exercises_to_recommend: int = 1, truly_random = False, bad_recommendation_limit: int = 3, k_neighbours: int = 5, distance_units: str = None, equipment_weight_units: str = None):
    exercises: list[RecommendedExercise] = []

    # TODO: implement factors that affect a recommendation e.g. user's daily mood/motivation, etc.
    # TODO: generate points based on given recommendation
    # TODO: handle the case where the user has NO logged exercises and/or NO recommended exercises

    '''
    algorithm: 
    
    BEGIN 

    - set bad_recommendation counter to 0
    - generate a random exercise from all exercise objects
    - get all logged and recommended exercises for given user and given exercise
    - if (proportion of good_recommendation >= 40%) OR (number of recommended_exercises + logged_exercises < 5), continue OTHERWISE repeat from 2 lines above

    if truly_random:
    - set the following to be random integers within the given range (if applicable to given exercise):
    - sets: [1, 5]
    - reps: [1, 15]
    - distance: [1, 10]
    - duration (in minutes): [1, 20]

    if not truly_random:
    - set the following to be within the given range (if applicable to given exercise):
    - sets: [1, ROUND(AVERAGE(exercise_history.sets) * random_range([0.8, 1.2]))]
    - reps: [1, ROUND(AVERAGE(exercise_history.reps WHERE exercise_history.sets >= sets - 1))]
    - distance: [1, ROUND(AVERAGE(exercise_history.distance) * random_range([0.7, 1.3]))]
    - duration (in minutes): [1, ROUND(AVERAGE(exercise_history.duration) * random_range([0.8, 1.2]))]
    - equipment_weight: [1, ROUND(AVERAGE(exercise_history.equipment_weight) * random_range([0.9, 1.3]))]

    - combine the attributes into a given exercise
    - run through the ML model for recommending an exercise
    
    if the recommendation is "bad":
    - increment bad_recommendation counter by 1
    ----- if equal to 3, start from BEGIN again
    ----- if not equal to 3, repeat "if truly_random or not" section
    
    if the recommendation is "good":
    - recommend the exercise
    - add it to exercises array

    END
    '''

    for _ in range(exercises_to_recommend):
        recommended = False
        recommendation_attempts = 0 # give up after e.g. 20 failed recommendation attempts

        while not recommended and recommendation_attempts < 20:
            recommended_exercise = RecommendedExercise(
                user=user
            )

            # algorithm begins
            bad_recommendations = 0

            # get the random exercise (finds a random primary key from all possible primary keys)
            possible_pks = Exercise.objects.values_list('pk', flat=True)

            while bad_recommendations < bad_recommendation_limit:
                can_continue = False
                exercise = Exercise()
                while not can_continue:
                    exercise = Exercise.objects.get(pk=random.choice(possible_pks))

                    all_recommended_exercises = RecommendedExercise.objects.filter(user=user, exercise=exercise)
                    all_logged_exercises = LoggedExercise.objects.filter(user=user, exercise=exercise)

                    can_continue = \
                        (all_recommended_exercises.__len__() + all_logged_exercises.__len__() < 5) or \
                        (all_recommended_exercises.filter(good_recommendation=True).__len__() / all_recommended_exercises.__len__() > 0.6)

                recommended_exercise.exercise = exercise
                if truly_random:
                    recommended_exercise.sets = random.randint(1, 5)
                    recommended_exercise.reps = random.randint(1, 15)
                    recommended_exercise.distance = random.randint(10, 100) / 10.0
                    recommended_exercise.duration = timedelta(minutes=random.randint(1, 20))
                else:
                    # since duration is a timedelta, avg has to be handled differently
                    all_durations = list(filter(lambda x: x is not None, list(all_logged_exercises.values_list('duration', flat=True)))) # remove all None instances of all duration values
                    all_duration_mins = [x.total_seconds() / 60.0 for x in all_durations] if len(all_durations) > 0 else [0]
                    minutes = \
                        round(np.mean(all_duration_mins) * random.uniform(0.8, 1.2), 2) \
                        if all_duration_mins != [0] \
                        else None
                    if minutes == None: minutes = 0
                    recommended_exercise.duration = timedelta(hours=minutes//60, minutes=floor(minutes%60), seconds=((minutes % 1) * 60) // 1) \

                    # TODO: factor in user mood when it comes to the random multiplier at the end

                    recommended_exercise.sets = \
                        round((all_logged_exercises.aggregate(Avg("sets", default=1))["sets__avg"]) * random.uniform(0.8, 1.2)) \
                        if all_logged_exercises.aggregate(Avg("sets"))["sets__avg"] != None \
                        else None
                    
                    recommended_exercise.reps = \
                        round((all_logged_exercises.filter(sets__gte=recommended_exercise.sets-1).aggregate(Avg("reps", default=1))["reps__avg"]) * random.uniform(0.9, 1.2)) \
                        if all_logged_exercises.aggregate(Avg("reps"))["reps__avg"] != None \
                        else None

                    recommended_exercise.distance = \
                        round((all_logged_exercises.aggregate(Avg("distance", default=1))["distance__avg"]) * random.uniform(0.7, 1.3)) \
                        if all_logged_exercises.aggregate(Avg("distance"))["distance__avg"] != None \
                        else None
                    # set distance units to given units or KM by default
                    if recommended_exercise.distance:
                        recommended_exercise.distance_units = distance_units if distance_units != "" else "km"

                    # sets equipment weight range between median of all recorded weights and maximum possible weight
                    all_equipment_weights = list(filter(lambda x: x is not None, list(all_logged_exercises.filter(equipment_weight_units=(equipment_weight_units or "kg")).values_list('equipment_weight', flat=True))))
                    if len(all_equipment_weights) > 0:
                        flattened = []
                        for w in all_equipment_weights:
                            for w2 in w:
                                flattened.append(w2)

                        median_weight = round(median_low(flattened) * random.uniform(0.9, 1.1))
                        max_weight = round(max([max(w) for w in all_equipment_weights]) * random.uniform(1, 1.2)) # the maximum recorded weight across all exercises

                        recommended_exercise.equipment_weight = \
                            np.linspace(start=median_weight, stop=max_weight, num=(recommended_exercise.sets or 1)).round().tolist()                        

                    if recommended_exercise.equipment_weight:
                        recommended_exercise.equipment_weight_units = equipment_weight_units if equipment_weight_units != "" else "kg"

                # convert all existing recommended exercises into a dataframe
                # treats all existing logged exercises as good recommendations
                rec_list = \
                    [pd.Series(list(ex.__todict__().values()),index=pd.MultiIndex.from_tuples(ex.__todict__().keys())) for ex in all_recommended_exercises] \
                    + [pd.Series(list(ex.__todict__().values()),index=pd.MultiIndex.from_tuples(ex.__todict__().keys())) for ex in all_logged_exercises] \
                    + [pd.Series(recommended_exercise.__todict__().values(), index=pd.MultiIndex.from_tuples(recommended_exercise.__todict__().keys()))]
                df = pd.DataFrame(rec_list)

                # run a k-means nearest neighbours model with the above recommended exercise

                # go up to the last one as the final value is the one we want to fit
                x = df.iloc[:-1,:-1].values # all other attributes
                y = df.iloc[:-1,-1].values # the "good" attribute

                if len(rec_list) > 1:
                    # start off with 5 neighbours,
                    # can be tweaked, may even set to a proportion of the dataset
                    k_means = KNeighborsClassifier(n_neighbors = (5 if len(rec_list) > 5 else len(rec_list) - 1))
                    k_means.fit(x, y) # fit the model to all recommended exercises for that user

                    # if the predicted output is good then add it, if not repeat the above
                    prediction = k_means.predict(df.iloc[-1,:-1].values.reshape(1, -1)) # predict the given recommended exercise
                else:
                    prediction = 1 # if there is no training data for the model, just assume it to be true, the user can always request a new exercise
                    # this does mean a brand new user will have completely random recommendations
                    # TODO: find a better solution than this len() check

                if prediction == 1:
                    exercises.append(recommended_exercise)
                    recommended_exercise.save()
                    recommended = True
                    break
                else:
                    bad_recommendations += 1

            recommendation_attempts += 1

    serialized_exercises = []
    for rec_ex in exercises:
        serialized_model = dict()

        # goes through every object in the recommended exercise object
        # if it needs formatting/displaying in the serialized_model, format then add
        # excludes all null values
        for key, value in model_to_dict(rec_ex).items():
            if value != None and value != []:
                match(key):
                    case "user": pass # don't need the username as that gets sent into the request anyways
                    case "good_recommendation": pass # don't need to return that it's a good recommendation, they always will be by default
                    case "duration": serialized_model[key] = value.__str__() # SPECIFICALLY FOR FORMATTING PURPOSES, IT IS HARD TO UNDERSTAND ON ITS OWN
                    case "datetime_recommended": serialized_model[key] = value.__str__() # formatting purposes too
                    case "exercise": serialized_model["ex_name"] = Exercise.objects.get(id=value).ex_name
                    case _:
                        serialized_model[key] = value

        serialized_exercises.append(serialized_model)

    return JsonResponse(serialized_exercises, safe=False)


# Create your views here.
class CreateAccountView(generics.CreateAPIView):
    serializer_class = UserSerializer

    # validates given email and username, checks given name within database and saves user data as unverified if valid
    def post(self, request, *args, **kwargs):
        if type(request.data) is not dict:
            return api_error("Invalid request type.")
        try:
            if validate_email(request.data['email']) \
                    and validate_username(request.data['username']):
                first_name = check_name(request.data['first_name'])
                last_name = check_name(request.data['last_name'])

                # check to find a user with given email
                if User.objects.filter(email=request.data['email']).__len__() > 0:
                    return api_error("Email already exists on a user.")

                user = User.objects.create_user(email=request.data['email'],
                                                password=check_password(request.data['password']),
                                                username=request.data['username'])
                user.first_name = first_name
                user.last_name = last_name
                user.save()

                # sets the users verification status to false
                verified = VerifiedUser(
                    user=user
                )
                verified.save()

                # responses for valid/invalid input of user
                return api_success({
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email,
                    "verified": verified.verified
                })
            else:
                return api_error("Invalid email or username.")
        except IntegrityError:
            return api_error("Username already exists. Please try again.")
        except KeyError as keyErr:
            return api_error('{} is missing.'.format(keyErr.__str__()))
        except (WeakPasswordError, InvalidNameException, TypeError) as error:
            return api_error(error.__str__())

    def delete(self, request, *args, **kwargs):
        if type(request.data) is not dict:
            return api_error("Invalid request type.")
        
        if 'password' not in request.data or 'email' not in request.data or 'username' not in request.data:
                return api_error("Invalid Entry")
        
        try:
            user_pass = request.data.get('password')

            #get the user from email
            email_user = User.objects.get(email=request.data.get('email'))
            #get the user from username
            username_user = User.objects.get(username=request.data.get('username'))

            #checking if the user is in the database
            if not email_user or not username_user:
                return api_error("User not found")
            
            #chceks if the users from email and username match
            if email_user.id != username_user.id:
                return api_error("Username does not match email")
            
            target_user_id = email_user.id
            
            if not email_user.check_password(user_pass):
                return api_error("Password does not match username/email")
            
            User.objects.filter(id=target_user_id).delete()

            return api_success(f"User account {target_user_id} deleted succesfully")

        except IntegrityError:
            return api_error("Incorrect Details")

class LoginView(APIView):
    def post(self, request):
        identifier = request.data.get('username') or request.data.get('email')  # Check if username or email is provided
        password = request.data.get('password')

        if not identifier or not password:
            return api_error("Username/Email and password are required")

        # Try to find the user by username or email
        # cannot login with email for some reason so we have to get the username via
        user = None
        if '@' in identifier:  # Check if the identifier is an email
            try:
                identifier = User.objects.get(email=identifier).username
            except User.DoesNotExist:
                return api_error("User not found with given email.")
            except User.MultipleObjectsReturned:
                return api_error("Multiple users found with given email.")
            
        user = authenticate(request=request, username=identifier, password=password)

        # If user found and authenticated
        if user:
            # finds a verification object for the given user
            # if a verification cannot be found, create a new one as false but still return same invalid error.
            try:
                if not VerifiedUser.objects.get(user=user).verified:            
                    return api_error("User not verified.")
            except VerifiedUser.DoesNotExist:
                verified = VerifiedUser(
                    user=user
                )
                verified.save()
                return api_error("User not verified.")

            if user.check_password(password):
                tokens = get_tokens_for_user(user)  # Generate JWT tokens
                return api_success({
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email,
                    "token": tokens['access'],  # Return access token for authentication
                    "refresh_token": tokens['refresh'],  # Refresh token for re-authentication
                })
            else:
                return api_error("Incorrect password.")
        else:
            return api_error("Invalid username or password.")


class GenerateOTPView(generics.CreateAPIView):
    serializer_class = OTPSerializer

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
        target_user: User | Response = get_user_by_email_username(request)

        if type(target_user) == Response:
            return target_user

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

            # retrieves OTP or creates a new one and deletes exsisting
            new_otp: OTP | None = None
            try:
                new_otp = OTP.objects.get(user=target_user)
            except OTP.DoesNotExist:
                new_otp = OTP(user=target_user)
            except OTP.MultipleObjectsReturned:
                # if there are somehow multiple instances of an OTP for a specific user
                # simplest option is to cull all existing entries and create a new one
                OTP.objects.get(user=target_user).delete()
                new_otp = OTP(user=target_user)

            new_otp.otp = otp
            new_otp.created_at = timezone.now()
            new_otp.expiry_time = new_otp.created_at + timezone.timedelta(minutes=5)
            print(new_otp.expiry_time)
            new_otp.verified = False

            # MAKE SURE TO SAVE WHEN UPDATING. 15 minutes of bugfixing to find out objects dont save without this lol
            new_otp.save()

            # returns all the data from the OTP.
            # "user" displays the username as User objects will not be displayed in a JSON format for security reasons, 
            return api_success("OTP sent.")
        except smtplib.SMTPException:
            return api_error("Email failed to send.")


class ValidateOTPView(generics.CreateAPIView):
    serializer_class = OTPSerializer

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
        target_user: User | Response = get_user_by_email_username(request)

        if type(target_user) == Response:
            return target_user

        # determines if an OTP was included
        if "otp" not in request.data:
            return api_error("No OTP was provided.")

        # gathers the OTP data for the user
        stored_otp = OTP.objects.get(user=target_user)

        # converts the OTP to a string if the type is numeric/integer
        # should never happen but extra check
        if type(request.data["otp"]) == int:
            request.data["otp"] = str(request.data["otp"])

        # checks if the OTP has passed expiry
        if timezone.now() > stored_otp.expiry_time:
            return api_error(f"The OTP has expired. Please request a new OTP.")

        if request.data["otp"].strip() == stored_otp.otp:
            # checks if the OTP has already been entered before
            if stored_otp.verified: return api_error("This OTP has already been entered before.")

            stored_otp.verified = True
            stored_otp.save()

            # set the user's account status to valid regardless of what the OTP was used for
            try:
                verified = VerifiedUser.objects.get(user=target_user)
                verified.verified = True
                verified.save()
            except VerifiedUser.DoesNotExist:
                verified = VerifiedUser(
                    user=target_user,
                    verified=True
                )
                verified.save()

            return api_success("success")
        else:
            return api_error("The OTP you entered is incorrect.")
        
class ResetPasswordView(generics.CreateAPIView):
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        target_user: User | Response = get_user_by_email_username(request)

        if type(target_user) == Response:
            return target_user

        # checks if the user has verified their OTP before continuing
        if not (OTP.objects.get(user=target_user).verified):
            return api_error("OTP not verified. Validate or request another.")
                       
        new_password = ""
        confirm_password = ""

        # checks given new password for matching confirmation and different from current password in database
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
            target_user.set_password(raw_password=new_password)
            target_user.save()

            # sets the current OTP to become invalid, otherwise this would make the user able to change their password an unlimited amount of times through the API
            # while not possible in the app as changing the password redirects the user to the login/home screen
            # very rare scenario but good for security
            currentOTP: OTP = OTP.objects.get(user=target_user)
            currentOTP.verified = False
            currentOTP.save()

            # response if password is too weak
            return api_success("Password Successfully Changed")
        except WeakPasswordError:
            return api_error("New password is too weak.")


class ExerciseView(generics.CreateAPIView):
    serializer_class = ExerciseSerializer
    # valid inputs for exercise variables stored in database
    exercise_type = ["Muscle" ,"Cardio","Flexibility"]
    body_area_types = ["Back", "Cardio", "Chest", "Lower Arms", "Lower Legs", "Neck", "Shoulders", "Upper Arms", "Upper Legs", "Core", "Flexibility"]
    muscle_types = ["Abdominals", "Abductors", "Abs", "Adductors", "Ankle Stabilizers", "Ankles", "Back", "Biceps", "Brachialis", "Cavles", "Cardio",
                    "Chest", "Core", "Deltoids", "Delts", "Feet", "Forearms", "Glutes", "Grip Muscles", "Groin", "Hamstrings", "Hands", "Hip Flexors",
                    "Inner Thighs", "Latissimus Dorsi", "Lats", "Levator Scapulae", "Lower Abs", "Lower Back", "Obliques", "Pectorals", "Quadriceps", "Quads",
                    "Rear Deltoids", "Rhomboids", "Rotator Cuff", "Serratus Anterior", "Shins", "Shoulders", "Soleus", "Spine", "Sternocleidomastoid",
                    "Trapezius", "Traps", "Triceps", "Upper Back", "Upper Chest", "Wrist Extensors", "Wrist Flexors", "Wrists"]

    def post(self, request, *args, **kwargs):
        # if no exercise objects, generate all from csv file
        if Exercise.objects.count() == 0:
            self.ExerciseFile()

        exercise: Exercise
        # response if one of the exercise fields are empty
        if 'ex_name' not in request.data or 'ex_type' not in request.data or 'ex_body_area' not in request.data or 'equipment_needed' not in request.data:
            return api_error("Necessary Field(s) are empty")

        ex_name = request.data['ex_name']
        ex_type = request.data['ex_type']
        ex_body_area = request.data['ex_body_area']
        equipment_needed = request.data['equipment_needed']

        # checks if target and secondary muscle inputs are valid or returns none
        if 'ex_target_muscle' in request.data:
            ex_target_muscle = request.data['ex_target_muscle']
        else:
            ex_target_muscle = "none"
        if 'ex_secondary_muscle_1' in request.data:
            ex_secondary_muscle_1 = request.data['ex_secondary_muscle_1']
        else:
            ex_secondary_muscle_1 = "none"
        if 'ex_secondary_muscle_2' in request.data:
            ex_secondary_muscle_2 = request.data['ex_secondary_muscle_2']


        # validates target muscle input
        if ex_type == "Muscle":
            if ex_target_muscle == "none":
                return api_error("Strength exercises must have at least 1 target muscle")
            if ex_target_muscle not in self.muscle_types or ex_secondary_muscle_1 not in self.muscle_types or ex_secondary_muscle_2 not in self.muscle_types:
                return api_error("Invalid Muscle Type")

        # validates exercise type input
        if ex_type not in self.exercise_type:
            return api_error("Invalid Exercise Type")

        # validates body area input
        if ex_body_area not in self.body_area_types:
            return api_error("Invalid Body Area Type")

        # creates Exercise instance and saves to database
        exercise = Exercise(
            ex_name=ex_name,
            ex_type=ex_type,
            ex_body_area=ex_body_area,
            equipment_needed=equipment_needed,
            ex_target_muscle=ex_target_muscle,
            ex_secondary_muscle_1=ex_secondary_muscle_1,
            ex_secondary_muscle_2=ex_secondary_muscle_2
        )
        exercise.save()

        # success response for created Exercise instance
        return api_success({
            "ex_name": exercise.ex_name,
            "ex_type": exercise.ex_type,
            "ex_body_area": exercise.ex_body_area,
            "equipment_needed": exercise.equipment_needed,
            "ex_target_muscle": exercise.ex_target_muscle,
            "ex_secondary_muscle_1": exercise.ex_secondary_muscle_1,
            "ex_secondary_muscle_2": ex_secondary_muscle_2
        })


    # given parameters equal to ex_type, filters all exercises for values
    def get(self, request, *args, **kwargs):
        # if no exercise objects, generate all from csv file
        if Exercise.objects.count() == 0:
            self.ExerciseFile()

        # every single Exercise object
        query_set = Exercise.objects.values()
    
        # returns an error if there are any filter attributes not known
        # while unknown attributes could just be ignored, best to not have them altogether
        all_exercise_fields = [f.name for f in Exercise._meta.get_fields()]
        for attribute in request.GET.keys():
            if attribute not in all_exercise_fields and attribute not in ['limit', 'offset']:
                return api_error("Unexpected filter name encountered.")

        # Apply filters based on query parameters in GET request
        for attribute in all_exercise_fields:
            if attribute in request.GET:
                filter_value = request.GET[attribute]
                if filter_value:
                    if attribute == "ex_name":
                        query_set = query_set.filter(ex_name__icontains=filter_value)
                    elif attribute == "ex_type":
                        query_set = query_set.filter(ex_type=filter_value)
                    elif attribute == "ex_body_area":
                        query_set = query_set.filter(ex_body_area=filter_value)
                    elif attribute == "equipment_needed":
                        query_set = query_set.filter(equipment_needed=filter_value)
                    elif attribute == "ex_target_muscle":
                        query_set = query_set.filter(ex_target_muscle=filter_value)
                    elif attribute == "ex_secondary_muscle_1":
                        query_set = query_set.filter(ex_secondary_muscle_1=filter_value)
                    elif attribute == "ex_secondary_muscle_2":
                        query_set = query_set.filter(ex_secondary_muscle_2=filter_value)

        # Pagination with limit and offset
        try:
            limit = int(request.GET.get('limit', 20))  # Default to 20 if not provided
            offset = int(request.GET.get('offset', 0))  # Default to 0 if not provided
            if limit < 1 or offset < 0:
                raise ValueError
        except ValueError:
            return api_error("Invalid pagination parameters: limit and offset must be positive integers.")

        # Create the paginator with the limit value
        paginator = Paginator(query_set, limit)

        # Calculate the page number from the offset
        page_number = (offset // limit) + 1

        try:
            exercises_page = paginator.page(page_number)
        except PageNotAnInteger:
            # If page number is not an integer, return first page
            exercises_page = paginator.page(1)
        except EmptyPage:
            # If page is out of range, return empty result
            exercises_page = paginator.page(paginator.num_pages)

        # Return paginated exercises
        return JsonResponse(list(exercises_page.object_list.values()), safe=False)

    def ExerciseFile(self):
        exercise: Exercise

        exercise_list = open('fitfocus_exercise_list.csv')
        csv_reader = csv.reader(exercise_list)
        rows = list(csv_reader)

        for i in range(1, len(rows)):
            exercise = Exercise(
                ex_name=rows[i][1],
                ex_type=rows[i][0],
                ex_body_area=rows[i][2],
                equipment_needed=rows[i][6],
                ex_target_muscle=rows[i][3],
                ex_secondary_muscle_1=rows[i][4],
                ex_secondary_muscle_2=rows[i][5]
            )
            exercise.save()
        exercise_list.close()

class LogExerciseView(generics.CreateAPIView):
    serializer_class = LoggedExerciseSerializer


    # retrieves target user and target exercise from username
    def post(self, request, *args, **kwargs):
        print("Headers:", request.headers)
        print("Body:", request.body.decode('utf-8'))
        try:
        # Ensure request.data is a dictionary
            data = request.data
            if not data:
                return api_error("No data provided.")

        except json.JSONDecodeError:
            return api_error("Invalid JSON format.")

    # Check what data is being received
        print("Request Data:", data)

        target_user = get_user_by_email_username(request)
        if type(target_user) == Response: return target_user
        target_exercise = get_exercise_by_name(request)
        if type(target_exercise) == Response: return target_exercise

        # creates LoggedExercise instance to log exercise in database
        logged_exercise = LoggedExercise(
            user=target_user,
            exercise=target_exercise,
            date_logged=request.data.get('date_logged', None),
            time_logged=request.data.get('time_logged', None),
            sets=request.data.get('sets', None),
            reps=request.data.get('reps', None),
            distance=request.data.get('distance', None),
            distance_units=request.data.get('distance_units', None),
            duration=pd.Timedelta("0 days " + request.data.get('duration', "")).to_pytimedelta(), # duration should be of format [x]hr[y]m[z]s
            equipment_weight=request.data.get('equipment_weight', None),
            equipment_weight_units=request.data.get('equipment_weight_units', None)
        )

        # if timedelta is empty, set it to None
        if logged_exercise.duration == timedelta(days=0): 
            logged_exercise.duration = None

        # if distance is present, should also have units
        if logged_exercise.distance and not logged_exercise.distance_units:
            return api_error("Distance needs a unit.")

        if logged_exercise.equipment_weight:
            # if equipment_weight is present but not sets, auto-assign sets to the length of the list
            if not logged_exercise.sets:
                logged_exercise.sets = sum([1 for _ in logged_exercise.equipment_weight])

            # if equipment_weight is present, should also have units
            if not logged_exercise.equipment_weight_units:
                return api_error("Weights used need unit(s).")
        
        if logged_exercise.date_logged is None:
            logged_exercise.date_logged = timezone.now().date()

        # validates inputs for logged exercise and saves if valid

        postable = False
        for attribute in ['sets', 'reps', 'distance', 'duration', 'equipment_weight']:
            if request.data.get(attribute) is not None:
                postable = True
                break
        if not postable:
            return api_error("Exercise log must contain some exercise information.")
        
        logged_exercise.save()

        return api_success("Exercised Logged!")
    
    def get(self, request, *args, **kwargs):
        # every single LoggedExercise object
        query_set = LoggedExercise.objects.values()
    
        # returns an error if there are any filter attributes not known
        # while unknown attributes could just be ignored, best to not have them altogether
        # needed for filtering by a certain username
        all_fields = [f.name for f in LoggedExercise._meta.get_fields()] + ["username", "email", "ex_name"]
        for attribute in request.data.keys():
            if attribute not in all_fields:
                return api_error("Unexpected filter name encountered.")
            
        # makes appropriate filters based on exercise attributes
        for attribute in all_fields:
            if attribute in request.query_params.keys():
                match(attribute):
                    case "date_logged__gt": query_set = query_set.filter(date_logged__gt=request.query_params["date_logged__gt"])
                    case "date_logged__lte": query_set = query_set.filter(date_logged__lte=request.query_params["date_logged__lte"])
                    case "username": query_set = query_set.filter(user=User.objects.get(username=request.query_params["username"]))
                    case "email": query_set = query_set.filter(user=User.objects.get(email=request.query_params["email"]))
                    case "ex_name": query_set = query_set.filter(exercise=Exercise.objects.get(ex_name=request.query_params["ex_name"]))
                    case "date_logged": query_set = query_set.filter(date_logged=request.query_params["date_logged"])
                    case "time_logged": query_set = query_set.filter(time_logged=request.query_params["time_logged"])
                    case "sets": query_set = query_set.filter(sets=request.query_params["sets"])
                    case "reps": query_set = query_set.filter(reps=request.query_params["reps"])
                    case "distance": query_set = query_set.filter(distance=request.query_params["distance"])
                    case "distance_units": query_set = query_set.filter(distance_units=request.query_params["distance_units"])
                    case "duration": query_set = query_set.filter(duration=request.query_params["duration"])
                    case "equipment_weight": query_set = query_set.filter(equipment_weight=request.query_params["equipment_weight"])
                    case "equipment_weight_units": query_set = query_set.filter(equipment_weight_units=request.query_params["equipment_weight_units"])
                    case _:
                        return api_error("Attribute not accounted for in filter.")

        # return filtered queryset
        # TODO: format to make it a normal display:
        # -- dont post any null values
        # -- don't display user or exercise id, just exercise name and username
        raw_response = JsonResponse(list(query_set), safe=False)
        filtered_response = []

        # only adds any non-null values
        for log in json.loads(raw_response.content.decode('utf8').replace("'", '"')):
            response = {}
            for key, value in log.items():
                if value != None and key != "id":
                    if key == "user_id":
                        response["username"] = User.objects.get(id=value).username
                    elif key == "exercise_id":
                        response["exercise"] = Exercise.objects.get(id=value).ex_name
                    else:
                        response[key] = value
            filtered_response.append(response)

        return JsonResponse(filtered_response, safe=False)

class RecommendExerciseView(generics.CreateAPIView):
    serializer_class = RecommendedExerciseSerializer

    # will generate recommended exercises based on the following:
    # - truly_random: boolean (default false) whether a new exercise will be 100% random or not
    # - user_identifier: email/username of the user to recommend for
    # - exercises_to_recommend: non-negative integer (default 1)
    # - k_neighbours: positive integer (default 5)
    def get(self, request, *args, **kwargs):
        truly_random: bool = False
        exercises_to_recommend: int = 1
        k_neighbours: int = 5
        target_user: User | Response = get_user_by_email_username(request)
        distance_units: str = "km"
        equipment_weight_units: str = "kg"

        if type(target_user) == Response: return target_user

        # sets the truly_random variable if it is present in the request
        if request.query_params.get("truly_random"):
            try:
                truly_random = request.query_params["truly_random"]
            except TypeError:
                return api_error("truly_random must be a boolean.")
        else:
            if request.data.get("truly_random"):
                try:
                    truly_random = request.data["truly_random"]
                except TypeError:
                    return api_error("truly_random must be a boolean.")
            
        # sets the exercises_to_recommend variable if it is present in the request
        if request.query_params.get("exercises_to_recommend"):
            try:
                exercises_to_recommend = request.query_params["exercises_to_recommend"]
                if exercises_to_recommend < 1: return api_error("exercises_to_recommend must be at least 1.")
            except TypeError as err:
                print(err.__str__())
                return api_error("exercises_to_recommend must be an integer.")
        else:
            if request.data.get("exercises_to_recommend"):
                try:
                    exercises_to_recommend = request.data["exercises_to_recommend"]
                    if exercises_to_recommend < 1: return api_error("exercises_to_recommend must be at least 1.")
                except TypeError as err:
                    print(err.__str__())
                    return api_error("exercises_to_recommend must be an integer.")
            
        # sets the k_neighbours variable if it is present in the request
        if request.query_params.get("k_neighbours"):
            try:
                k_neighbours = request.query_params["k_neighbours"]
                if k_neighbours < 1: return api_error("k_neighbours must be at least 1.")
            except TypeError:
                return api_error("k_neighbours must be an integer.")
        else:
            if request.data.get("k_neighbours"):
                try:
                    k_neighbours = request.data["k_neighbours"]
                    if k_neighbours < 1: return api_error("k_neighbours must be at least 1.")
                except TypeError:
                    return api_error("k_neighbours must be an integer.")
            
        # sets the distance_units variable if it is present in the request
        if request.query_params.get("distance_units"):
            try:
                distance_units = request.query_params["distance_units"]
            except TypeError:
                return api_error("distance_units must be a string.")
        else:
            if request.data.get("distance_units"):
                try:
                    distance_units = request.query_params["distance_units"]
                except TypeError:
                    return api_error("distance_units must be a string.")
            
        # sets the equipment_weight_units variable if it is present in the request
        if request.query_params.get("equipment_weight_units"):
            try:
                equipment_weight_units = request.query_params["equipment_weight_units"]
            except TypeError:
                return api_error("equipment_weight_units must be a string.")
        else:
            if request.data.get("equipment_weight_units"):
                try:
                    equipment_weight_units = request.query_params["equipment_weight_units"]
                except TypeError:
                    return api_error("equipment_weight_units must be a string.")
                
        return recommend_exercises(
            user=target_user, 
            exercises_to_recommend=exercises_to_recommend, 
            truly_random=truly_random, 
            k_neighbours=k_neighbours,
            distance_units=distance_units,
            equipment_weight_units=equipment_weight_units
        )
    
class UpdateRecommendedExerciseView(generics.CreateAPIView):
    serializer_class = RecommendedExerciseSerializer

    def post(self, request, *args, **kwargs):
        print(request.data)
        rec_ex_id = request.data.get("rec_ex_id")
        good_recommendation = request.data.get("good_recommendation")

        if rec_ex_id == None: return api_error("A valid ID for the recommended exercise must be provided.")
        if good_recommendation == None: return api_error("good_recommendation must be provided.")

        try:
            rec_ex = RecommendedExercise.objects.get(id=rec_ex_id)
            rec_ex.good_recommendation = good_recommendation if type(good_recommendation) == bool else True
            rec_ex.save()

            return api_success("Exercise successfully updated.")
        except RecommendedExercise.DoesNotExist:
            return api_error("A recommended exercise could not be found.")
        except RecommendedExercise.MultipleObjectsReturned:
            return api_error("Multiple recommended exercises were found.") # should never happen

class ConsumableView(generics.CreateAPIView):
    serializer_class = ConsumableSerializer

    # handles creating OR updating a consumable based on the name
    def post(self, request, *args, **kwargs):
        keys = [
            "name",
            "sample_size",
            "sample_calories",
        ]
        check_all_required_keys_present(request, keys)

        try:
            consumable = Consumable.objects.get(name=request.data['name'])
        except Consumable.DoesNotExist:
            consumable = Consumable(name=request.data['name'])
        except Consumable.MultipleObjectsReturned:
            return api_error("Multiple ingredients with the same name were found.")

        # if the ingredient did not exist beforehand, the user passed through is made the owner of this ingredient
        consumable.sample_calories = request.data["sample_calories"]
        consumable.sample_macros = request.data.get("sample_macros")
        consumable.sample_size = request.data["sample_size"]
        consumable.sample_units = request.data.get("sample_units") or "serving"

        consumable.save()

        return api_success("Consumable created!")

'''
The LogConsumable view takes in the following parameters:
* refers to an optional parameter

- username/email: a string which should identify a single user (if they exist)
- consumable: a string, being the name of a consumable item,
- amount_logged: the amount of the consumable above that was consumed,
- date_logged: a string (date format YYYY-MM-DD), when the consumable was consumed
- calories_logged: an integer of the total calories logged for the given consumable
- *macros_logged: a dictionary (keys can only be from models.macro_keys, values are all numeric), containing the macronutrient total of the consumable
'''
class LogConsumableView(generics.CreateAPIView):
    serializer_class = LoggedConsumableSerializer

    def get(self, request, *args, **kwargs):
        logged_consumable_queryset = LoggedConsumable.objects.get_queryset()

        target_user = get_user_by_email_username(request)
        if type(target_user) == Response: return target_user
        logged_consumable_queryset = logged_consumable_queryset.filter(user=target_user)

        if request.query_params.get("date_logged"):
            logged_consumable_queryset = logged_consumable_queryset.filter(date_logged=request.query_params["date_logged"])


        serialized_consumables = []
        for consum in logged_consumable_queryset:
            serialized_model = dict()

            # goes through every object in the recommended exercise object
            # if it needs formatting/displaying in the serialized_model, format then add
            # excludes all null values
            for key, value in model_to_dict(consum).items():
                if value != None and value != []:
                    match(key):
                        case "id": pass
                        case "user": pass # don't need the username as that gets sent into the request anyways
                        case _:
                            serialized_model[key] = value

            serialized_consumables.append(serialized_model)

        return JsonResponse(serialized_consumables, safe=False)

    def post(self, request, *args, **kwargs):
        keys = [
            "consumable",
            "amount_logged",
            "date_logged",
            "calories_logged"
        ]

        for key in keys:
            if key not in list(request.data.keys()):
                return api_error(f"One or more API fields were not included in the request.")
            else:
                if request.data[key] == "" or request.data[key] == None:
                    return api_error(f"One or more required fields are empty.")

        target_user = get_user_by_email_username(request)
        if type(target_user) == Response: return target_user

        try:
            amount_logged = request.data.get("amount_logged") or 1

            new_consumable = False
            try:
                target_consumable = Consumable.objects.get(name=request.data["consumable"])
            except Consumable.DoesNotExist:
                new_consumable = True
                target_consumable = Consumable(
                    name=request.data["consumable"],
                    sample_units=request.data.get("sample_units") or "serving"
                )
            if new_consumable:
                target_consumable.sample_size = amount_logged
                target_consumable.sample_calories = int(request.data["calories_logged"]) # because the user will log an amount, set "1 serving" equal to the total calories / amount logged
                target_consumable.sample_macros = request.data.get("macros_logged")

                target_consumable.save()


            logged_consumable = LoggedConsumable(
                user=target_user,
                consumable=target_consumable, # index at 0 because get_or_create returns a tuple
                amount_logged=amount_logged if not new_consumable else 1, # return 1 serving of the newly created consumable when logged
                date_logged=request.data["date_logged"],
                calories_logged=request.data["calories_logged"],
            )
            if request.data.get("macros_logged"): logged_consumable.macros_logged = request.data["macros_logged"]

            logged_consumable.save()

            return api_success("Consumable logged!")
        except Exception as e:
            return api_error(e.__str__())

class RoutineListCreateView(generics.ListCreateAPIView):
    #Handles listing all routines and creating a new one.
    serializer_class = RoutineSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
    #Only return routines belonging to the logged-in user.
        return Routine.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        ##Associate the created routine with the logged-in user.
        serializer.save(user=self.request.user)


class RoutineDetailView(generics.RetrieveAPIView):
    #Handles retrieving a single routine.
    serializer_class = RoutineSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        #Only allow the user to retrieve their own routines.
        return Routine.objects.filter(user=self.request.user)

# Routine Update API View
class RoutineUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        routine = self.get_object()

        data = request.data.copy()
        if "name" not in data or not data["name"].strip():
            data["name"] = "My Routine"

        serializer = RoutineUpdateSerializer(routine, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_object(self):
        routine = Routine.objects.filter(user=self.request.user, pk=self.kwargs['pk']).first()
        if not routine:
            raise Http404("Routine not found or you do not have permission to edit it")
        return routine

# Routine Delete API View
class RoutineDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        routine = self.get_object()

        # Delete all related routine exercises
        routine_exercises = RoutineExercise.objects.filter(routine=routine)
        routine_exercises.delete()

        # Now delete the routine itself
        routine.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_object(self):
        routine = Routine.objects.filter(user=self.request.user, pk=self.kwargs['pk']).first()
        if not routine:
            raise Http404("Routine not found or you do not have permission to delete it")
        return routine

class RoutineExerciseListCreateView(generics.ListCreateAPIView):
    #Handles listing all RoutineExercise objects and creating new ones.
    queryset = RoutineExercise.objects.all()
    serializer_class = RoutineExerciseSerializer

    def get_queryset(self):
        #Filter exercises to only return those belonging to the logged-in user.
        return RoutineExercise.objects.filter(routine__user=self.request.user)


class RoutineExerciseDetailView(generics.RetrieveUpdateDestroyAPIView):
    # Handles retrieving, updating, or deleting a specific RoutineExercise.
    queryset = RoutineExercise.objects.all()
    serializer_class = RoutineExerciseSerializer

    def get_queryset(self):
        # Filter exercises so users can only modify their own routine exercises.
        return RoutineExercise.objects.filter(routine__user=self.request.user)

    def perform_destroy(self, instance):
        #When an exercise is deleted, shift the order of the remaining ones.
        routine = instance.routine
        order_deleted = instance.order

        # Delete the selected exercise
        instance.delete()

        # Shift all exercises that were below the deleted one
        RoutineExercise.objects.filter(
            routine=routine,
            order__gt=order_deleted  # Only update exercises that were below the deleted one
        ).update(order=F('order') - 1)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        new_order = request.data.get('order')

        if new_order is None or new_order == instance.order:
            return super().update(request, *args, **kwargs)  # No change needed

        routine = instance.routine

        # Shift exercises down if needed
        if new_order < instance.order:
            RoutineExercise.objects.filter(
                routine=routine,
                order__gte=new_order,
                order__lt=instance.order
            ).update(order=F('order') + 1)

        elif new_order > instance.order:
            RoutineExercise.objects.filter(
                routine=routine,
                order__gt=instance.order,
                order__lte=new_order
            ).update(order=F('order') - 1)

        # Update the instance's order
        instance.order = new_order
        instance.save()

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

class UserDataCreateView(generics.CreateAPIView):
    serializer_class = UserDataSerializer

    # NOTE: THIS CREATES A NEW OBJECT FOR EACH POST
    # this shouldn't happen, but isn't a problem because of user data cascade deletion
    # can be useful for tracking weight over time, but height and/or sex history should not be stored
    # TODO: potentially create another model for user weight and when that was logged, based off of this view
    def post(self, request, *args, **kwargs):
        target_user: User | Response = get_user_by_email_username(request)
        if type(target_user) == Response: return target_user

        user_data = UserData(user=target_user)
        try:
            user_data = UserData.objects.get(user=target_user)
        except UserData.DoesNotExist:
            user_data = UserData(user=target_user)
        except UserData.MultipleObjectsReturned:
            # delete all instances except the latest record
            latest = UserData.objects.filter(user=target_user).order_by("-id")[0]
            UserData.objects.filter(user=target_user).delete()

            latest.save()


        if request.data.get("user_age"):
            try:
                user_data.user_age = int(request.data["user_age"])
                if user_data.user_age < 1: raise TypeError
            except TypeError:
                return api_error("Age can only be a whole number >= 1")
        else:
            return api_error("No age was provided.")

        if request.data.get("user_sex"):
            if request.data["user_sex"] not in ["M", "F", "X"]:
                return api_error("User sex must be M, F, X or empty.")
            else:
                user_data.user_sex = request.data["user_sex"]

        if request.data.get("user_height"):
            try:
                user_data.user_height = float(request.data["user_height"])
                if user_data.user_height <= 0.0: raise TypeError
            except TypeError:
                return api_error("Height must be a positive number.")
        else:
            return api_error("No height was provided.")

        if request.data.get("user_height_units") != None:
            if request.data["user_height_units"] not in ["in", "cm"]:
                return api_error("Height units must be: \"in\" OR \"cm\".")
            else:
                user_data.user_height_units = request.data["user_height_units"]
        else:
            return api_error("No height units were provided.")

        if request.data.get("user_weight"):
            try:
                user_data.user_weight = float(request.data["user_weight"])
                if user_data.user_weight <= 0.0: raise TypeError
            except TypeError:
                return api_error("Weight must be positive.")

            if request.data.get("user_weight_units"):
                if request.data["user_weight_units"] not in ["lb", "kg"]:
                    return api_error("Weight units must be: \"lb\" OR \"kg\".")
                else:
                    user_data.user_weight_units = request.data["user_weight_units"]
            else:
                return api_error("Weight units must be provided for a weight.")

        if request.data.get("user_target_weight"):
            try:
                user_data.user_target_weight = float(request.data["user_target_weight"])
                if user_data.user_target_weight <= 0.0: raise ValueError
            except ValueError:
                return api_error("Target weight must be a positive number.")

        if request.data.get("user_body_goals"):
            if not isinstance(request.data["user_body_goals"], list):
                return api_error("Body goals must be given as a list.")
            else:
                user_data.user_body_goals = request.data["user_body_goals"]
        user_data.save()

        return JsonResponse(model_to_dict(user_data), safe=False)




class UserMoodView(generics.CreateAPIView):
    serializer_class = UserMoodSerializer

    def post(self, request, *args, **kwargs):
        target_user: User | Response = get_user_by_email_username(request)
        if type(target_user) == Response: return target_user

        user_mood = UserMood(user=target_user)

        if request.data.get("mood_level") != None:
            try:
                user_mood.mood_level = int(request.data["mood_level"])
                if user_mood.mood_level not in [-2, -1, 0, 1, 2]: raise TypeError
            except TypeError:
                return api_error("Mood level must be an integer between -2 and 2")
        else:
            return api_error("No mood was provided.")

        if request.data.get("datetime_recorded"):
            try:
                #user_mood.datetime_recorded = datetime(request.data["datetime_recorded"])
                user_mood.datetime_recorded = datetime.datetime.strptime(request.data["datetime_recorded"], "%Y-%m-%d %H:%M:%S")
            except TypeError:
                return api_error("DateTime is in the incorrect format")
        else:
            user_mood.datetime_recorded = timezone.now()

        user_mood.save()

        return api_success({
            "mood_level": user_mood.mood_level,
            "datetime_recorded": user_mood.datetime_recorded
        })

    def get(self, request, *args, **kwargs):
        user_mood_queryset = UserMood.objects.get_queryset()

        target_user: User | Response = get_user_by_email_username(request)
        if type(target_user) == Response: return target_user

        user_mood_queryset = user_mood_queryset.filter(user=target_user)

        if user_mood_queryset.order_by("datetime_recorded").__len__() > 0:
            latest_user_mood = user_mood_queryset.order_by("-datetime_recorded")[0]
        else:
            latest_user_mood = UserMood(
                user=target_user,
                mood_level=0,
                datetime_recorded=timezone.datetime.strptime("1970-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")
            )

            latest_user_mood.save()

        return Response({
            "mood_level": latest_user_mood.mood_level,
            "datetime_recorded" : timezone.datetime.strftime(latest_user_mood.datetime_recorded, "%Y-%m-%d %H:%M:%S"),
        })




class LogRoutineView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        logged_routine_id = request.data.get('id')
        if not logged_routine_id:
            return Response({"error": "Logged routine ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            logged_routine = LoggedRoutine.objects.get(id=logged_routine_id, user=request.user)
        except LoggedRoutine.DoesNotExist:
            return Response({"error": "Logged routine not found or you don't have permission to delete it."},
                            status=status.HTTP_404_NOT_FOUND)

        logged_routine.delete()
        return Response({"success": "Logged routine deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

    def get(self, request, *args, **kwargs):
        logged_routines = LoggedRoutine.objects.filter(user=request.user).order_by('-completed_at')
        serializer = LoggedRoutineSerializer(logged_routines, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        routine_id = request.data.get('routine_id')
        notes = request.data.get('notes', '')
        duration_str = request.data.get('duration', None)
        progress = request.data.get('progress', {})
        exercises_data = progress.get('exercises', [])

        # Convert routine duration if provided
        if duration_str:
            try:
                duration = pd.Timedelta("0 days " + duration_str).to_pytimedelta()
            except ValueError:
                return Response({"error": "Invalid duration format. Please use 'hh:mm:ss'."},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            duration = None

        try:
            routine = Routine.objects.get(id=routine_id, user=request.user)
        except Routine.DoesNotExist:
            return Response({"error": "Routine not found or you do not have permission to log it."},
                            status=status.HTTP_404_NOT_FOUND)

        # Validate all exercises first
        validated_exercises = []
        for exercise_data in exercises_data:
            exercise_id = exercise_data.get('exercise_id')
            sets = exercise_data.get('sets')
            reps = exercise_data.get('reps')
            distance = exercise_data.get('distance')
            distance_units = exercise_data.get('distance_units')
            time_str = exercise_data.get('duration')

            try:
                time = pd.Timedelta("0 days " + time_str).to_pytimedelta() if time_str else None
            except ValueError:
                return Response({"error": "Invalid exercise duration format. Please use 'hh:mm:ss'."},
                                status=status.HTTP_400_BAD_REQUEST)

            try:
                exercise = Exercise.objects.get(id=exercise_id)
            except Exercise.DoesNotExist:
                return Response({"error": f"Exercise {exercise_id} not found."}, status=status.HTTP_400_BAD_REQUEST)

            if exercise_id not in [r.exercise.id for r in routine.routine_exercises.all()]:
                return Response({"error": f"Exercise {exercise_id} is not part of this routine."},
                                status=status.HTTP_400_BAD_REQUEST)

            if exercise.ex_type == 'Cardio':
                if distance is None or not distance_units:
                    return Response({"error": f"Cardio exercise {exercise_id} missing distance or unit."},
                                    status=status.HTTP_400_BAD_REQUEST)
                if time is None:
                    return Response({"error": f"Cardio exercise {exercise_id} missing duration."},
                                    status=status.HTTP_400_BAD_REQUEST)
            else:
                if distance or distance_units:
                    return Response({"error": f"Distance is not required for strength exercise {exercise_id}."},
                                    status=status.HTTP_400_BAD_REQUEST)
                if sets is None or reps is None or not exercise_data.get('weight'):
                    return Response({"error": f"Strength exercise {exercise_id} missing sets, reps, or weight."},
                                    status=status.HTTP_400_BAD_REQUEST)

            # All validations passed for this exercise
            validated_exercises.append({
                'exercise': exercise,
                'sets': sets,
                'reps': reps,
                'distance': distance,
                'distance_units': distance_units,
                'duration': time,
            })

        # ✅ Everything valid — now save
        logged_routine = LoggedRoutine.objects.create(
            routine=routine,
            user=request.user,
            notes=notes,
            duration=duration,
            progress=progress
        )

        for ex in validated_exercises:
            LoggedExercise.objects.create(
                user=request.user,
                logged_routine=logged_routine,
                exercise=ex['exercise'],
                sets=ex['sets'],
                reps=ex['reps'],
                distance=ex['distance'],
                distance_units=ex['distance_units'],
                duration=ex['duration']
            )

        serializer = LoggedRoutineSerializer(logged_routine)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

        # Return the logged routine data with the appropriate serializer
        serializer = LoggedRoutineSerializer(logged_routine)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class ExerciseDetailView(RetrieveAPIView):
    queryset = Exercise.objects.all()
    serializer_class = ExerciseSerializer
    
class RecommendConsumableView(generics.CreateAPIView):
    serializer_class = ConsumableSerializer

    # TODO: be called if the size of the consumable database is 100 objects or less? to be decided
    def fill_consumable_dataset(self):
        with open("utils/food_data/food.json") as f:
            food_file_content: list[dict] = json.loads(f.read())

            print("loaded json file")
            
            progress_counter = 0
            progress_cap = len(food_file_content)

            for food in food_file_content:
                food_name: str = food["name"]

                # find a consumable with the given name in the dataset, if not, create a new one
                file_consumable = Consumable()
                try:
                    file_consumable = Consumable.objects.get(name=food_name)
                except:
                    file_consumable = Consumable(
                        name=food_name
                    )

                # update all the nutrition information
                file_consumable.sample_size = food["sample_size"]
                file_consumable.sample_units = food["sample_units"]
                file_consumable.sample_calories = food["sample_calories"]
                file_consumable.sample_macros = food["sample_macros"]

                # save the object
                file_consumable.save()

                # print a progress update every 10%(FOR DEBUGGING ONLY)
                progress_counter += 1
                if ((progress_counter - 1) / progress_cap) // 0.1 != (progress_counter / progress_cap) // 0.1:
                    print(f"file {int((progress_counter / progress_cap) // 0.1 * 10)}% complete")

            print("finished with json file")

        return api_success("dataset filled with foods")

    # not sure whether to make this a GET or POST function, input parameters etc
    # request includes the following attributes:
    # email/username - to identify the user
    # (OPTIONAL) consumables_to_recommend - number of consumables to recommend to the user (default 1)
    # (OPTIONAL) recommendation_date - date to look at when generating recommendation dataset (default today)
    def post(self, request):
        target_user: User | Response = get_user_by_email_username(request)
        if type(target_user) == Response: return target_user

        date_to_search: datetime.date = datetime.datetime.now().date().strftime("%Y-%m-%d")
        if request.data.get("date_to_search") != None:
            date_to_search = request.data["date_to_search"]

        # how the algorithm works:
        # - macro ratio = ratio between carbohydrates, protein and fat in that order.
        # ----- example: a 100g cooked chicken breast has 0g carbs, 31g protein, 3.6g fat
        # ----- this will return a ratio of 0:31:3.6 and will be converted to percentages
        # ----- so this will return 0:89.6:10.4, which will then get rounded to 0:90:10, (nearest integer)
        # - 1) looks at the user's goals and consumed foods for the given date (if not present in the HTTP request, assume to be current date)
        # - 2) will sum up the total calories, carbohydrates, protein and fat, and subtract them from recommended daily intake values. results in an "ideal" intake.
        # - this "ideal" intake will be multiplied by a decimal value, depending on:
        # ----- the time of day (to determine the portion size of the meal)
        # ----- the user's current mood/motivation (lower mood = less strict range of acceptable macro values)
        # - 3) takes a list of a random 10% sample of the consumables dataset, as well as every unique consumable logged by the user within the last 2 weeks
        # - 4) uses a 2D euclidean distance minimising algorithm to find the best consumable to recommend
        # - 5) returns the top X amount of meals with the least distance to this "ideal" intake
        # - X can be determined in the request input, if not specified, then will be 1.

        # 1)


        all_target_goal_types = [
            "Reducing Body Fat",
            "Increasing Body Fat",
            "Building Muscle Mass",
            "Body Maintenance",
            "Muscle Toning",
            "Boosting Metabolism"
        ]
        try:
            target_goals: list[str] = UserData.objects.get(user=target_user).user_body_goals
        except:
            target_goals = []

        # add current date's consumed meals
        target_date_consumed_macros: dict = {
            "calories": 0,
            "fat_g": 0,
            "protein_g": 0,
            "carbohydrates_g": 0
        }
        for logged_consumable in LoggedConsumable.objects.get_queryset():
            if logged_consumable.user == target_user and logged_consumable.date_logged.strftime("%Y-%m-%d") == date_to_search:
                for key in target_date_consumed_macros.keys():
                    if key == "calories": 
                        target_date_consumed_macros[key] += logged_consumable.calories_logged
                    else:
                        if type(logged_consumable.macros_logged) == dict:
                            if key in logged_consumable.macros_logged.keys():
                                target_date_consumed_macros[key] += logged_consumable.macros_logged[key]

        # 2)
        # recommended minimum calories: (Harris-Benedict equation)
        # - if the user has provided their weight:
        # ----- if the user is male: 88.362 + (13.397 * weight_kg) + (4.799 * height_cm) - (5.677 * age)
        # ----- else if the user is female: 447.593 + (9.247 * weight_kg) + (3.098 * height_cm) - (4.330 * age)
        # ----- else (other/don't want to say): take the average of the above 2
        # - else 2000

        recommended_daily_calories = 2000
        try:
            target_user_data = UserData.objects.get(user=target_user)

            if target_user_data.user_weight != None:
                weight_kg = target_user_data.user_weight if target_user_data.user_weight_units == "kg" else target_user_data.user_weight * 0.454 # converts to kg if weight is in lb
                height_cm = target_user_data.user_height if target_user_data.user_height_units == "cm" else target_user_data.user_weight * 2.54 # converts to cm if height is in inches 

                male_calories = 88.362 + (13.397 * weight_kg) + (4.799 * height_cm) - (5.677 * target_user_data.user_age)
                female_calories = 447.593 + (9.247 * weight_kg) + (3.098 * height_cm) - (4.330 * target_user_data.user_age)

                if target_user_data.user_sex[0] == "M":
                    recommended_daily_calories = int(male_calories)
                elif target_user_data.user_sex[0] == "F":
                    recommended_daily_calories = int(female_calories)
                else:
                    recommended_daily_calories = int((male_calories + female_calories) / 2)

        except:
            # if there is no user data, assume daily calories to be 2000
            pass

        # recommended daily macronutrients: (very heavily depends on user goals)
        # based on a normal diet, these are the proportion of CALORIES made up of nutrients
        recommended_daily_macros = {
            "carbs": 0.55, # where 1g carbs = 4 calories
            "protein": 0.25, # where 1g protein = 4 calories
            "fat": 0.2 # where 1g fat = 9 calories
        }

        for goal in target_goals:
            if goal in all_target_goal_types:
                match (goal):
                    case "Reducing Body Fat":
                        recommended_daily_macros["carbs"] -= 0.1
                        recommended_daily_macros["fat"] -= 0.05
                    case "Increasing Body Fat":
                        recommended_daily_macros["carbs"] += 0.1
                        recommended_daily_macros["fat"] += 0.05
                    case "Building Muscle Mass":
                        recommended_daily_macros["protein"] += 0.1
                        pass
                    case "Body Maintenance":
                        recommended_daily_macros["protein"] += 0.1
                        pass
                    case "Muscle Toning" | "Boosting Metabolism":
                        recommended_daily_macros["carbs"] -= 0.2
                        recommended_daily_macros["protein"] += 0.1
                        recommended_daily_macros["fat"] -= 0.1
                        pass

        recommended_daily_macros["carbs"] = max(0.2, recommended_daily_macros["carbs"]) # 0-carb diets may not be healthy, so keep this at a minimum of 20% caloric intake
        recommended_daily_macros["protein"] = max(0.1, recommended_daily_macros["protein"]) # always try and consume SOME protein
        recommended_daily_macros["fat"] = max(0, recommended_daily_macros["fat"]) # while fat is necessary, cutting all fat has a lot of upsides, and no 0-carb diet can make up for that
        
        # subtract consumed macros from recommended daily amounts to get MAXIMUM recommended intake for the meal
        # caps at 1* if the consumed amount is more than the recommended daily amount
        # * was goign to be 0, but division by 0 can occur later on so set to 1 for prevention
        max_calories = max(int(recommended_daily_calories - target_date_consumed_macros["calories"]), 1)
        max_carbs_g = max(int(recommended_daily_calories * recommended_daily_macros["carbs"] / 4 - target_date_consumed_macros["carbohydrates_g"]), 1)
        min_protein_g = max(int(recommended_daily_calories * recommended_daily_macros["protein"] / 4 - target_date_consumed_macros["protein_g"]), 1)
        max_fat_g = max(int(recommended_daily_calories * recommended_daily_macros["fat"] / 9 - target_date_consumed_macros["fat_g"]), 1)


        # given user mood and motivation level, multiply (or divide) the target intake by a factor
        # -2 = lower targets (multiply by 0.7-0.9)
        # 0 = keep the same 
        # 2 = higher targets (multiply by 1.1-1.3)

        user_mood = UserMoodView().get(request).data["mood_level"]
        mood_multipliers = {
            -2: 0.7, 
            -1: 0.9, 
            0: 1, 
            1: 1.1, 
            2: 1.3, 
        }

        # calories intentionally left out because macro per calorie ratio multiplier would be squared, can be too lenient
        max_carbs_g = int(max_carbs_g / mood_multipliers[user_mood])
        min_protein_g = int(min_protein_g * mood_multipliers[user_mood])
        max_fat_g = int(max_fat_g / mood_multipliers[user_mood])


        # try and estimate how many remaining meals to take, assuming 1 meal falls in the range of 400-600 calories (inclusive)
        # assumes a max of 3 meals per day
        remaining_meals = 1
        if max_calories > 600:
            while max_calories / remaining_meals > 600 and remaining_meals < 3:
                remaining_meals += 1

        max_calories = int(max_calories / remaining_meals)
        max_carbs_g = int(max_carbs_g / remaining_meals)
        min_protein_g = int(min_protein_g / remaining_meals)
        max_fat_g = int(max_fat_g / remaining_meals)


        print({
            "max_calories": max_calories,
            "max_carbs_g": max_carbs_g,
            "min_protein_g": min_protein_g,
            "max_fat_g": max_fat_g,
        })


        # 3)
        if Consumable.objects.count() < 100:
            self.fill_consumable_dataset()

        recommendation_meal_set: set[Consumable] = set()
        consumable_limit = Consumable.objects.count() // 10
        # because random.sample doesn't work, use this instead
        # every meal in the Consumable table has a 10% chance of being added
        # stops once 10% limit has been hit
        for meal in Consumable.objects.all():
            if randint(1, 10) == 1:
                recommendation_meal_set.add(meal)
                if len(recommendation_meal_set) == consumable_limit:
                    break

        for meal in LoggedConsumable.objects.filter(user=target_user).filter(date_logged__gte=timezone.datetime.strftime(timezone.now().__add__(timedelta(weeks=2)), "%Y-%m-%d")):
            recommendation_meal_set.add(meal.consumable)

        # cannot be subscripted, so convert set back to a list
        recommendation_meal_set = list(recommendation_meal_set)

        # 4)
        # HIGHER SCORE IS WORSE
        recommendation_dict: dict[str, float] = {}
        for meal in recommendation_meal_set:
            calorie_diff = (meal.sample_calories / max_calories) ** 2
            recommendation_dict[meal.name] = calorie_diff 


            if meal.sample_macros != None:
                if type(meal.sample_macros) == dict:
                    # TODO: TWEAK THESE THREE TO REDUCE SCORE FOR MULTIPLIER_VALUE BETWEEN 0.5-1.0
                    # TODO: TWEAK THESE TO INCREASE SCORE OUTSIDE OF THIS RANGE

                    if "protein_g" in meal.sample_macros:
                        if min_protein_g > 0.0:
                            multiplier_value = meal.sample_macros["protein_g"] / min_protein_g
                            if multiplier_value < 1.0:
                                if multiplier_value == 0:
                                    multiplier_value = 10000 # absurdly high but gets the point across
                                else:
                                    multiplier_value = 1 / multiplier_value

                            recommendation_dict[meal.name] += multiplier_value ** 2
                        else:
                            recommendation_dict[meal.name] += 4
                            

                    if "carbohydrates_g" in meal.sample_macros:
                        if max_carbs_g > 0.0:
                            multiplier_value = meal.sample_macros["carbohydrates_g"] - max_carbs_g
                            recommendation_dict[meal.name] += multiplier_value ** 2
                        else:
                            recommendation_dict[meal.name] += 4
                        

                    if "fat_g" in meal.sample_macros:
                        if max_fat_g > 0.0:
                            multiplier_value = meal.sample_macros["fat_g"] - max_fat_g
                            recommendation_dict[meal.name] += multiplier_value ** 2
                        else:
                            recommendation_dict[meal.name] += 4
                    else:
                        recommendation_dict[meal.name] += 1


                else:
                    recommendation_dict[meal.name] += 3
            else:
                # if no value for the 3 macros can be found, assume all to be 1, and add them on
                recommendation_dict[meal.name] += 3

        # 5)
        sorted_recommendation_dict = dict(sorted(recommendation_dict.items(), key=lambda item: item[1]))
        consumables_to_recommend = min(len(sorted_recommendation_dict), request.data.get("consumables_to_recommend", 1))

        final_recommendations = []
        for name in [*sorted_recommendation_dict]:
            if random.randint(1, 10) <= 8: # 80% chance of being added
                final_recommendations.append(
                    model_to_dict(
                        Consumable.objects.get(name=name),
                        exclude="logged_user"
                    )
                )
                if len(final_recommendations) == consumables_to_recommend:
                    break

        return JsonResponse(final_recommendations, safe=False)