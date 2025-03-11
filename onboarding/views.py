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

from django.contrib.auth.models import User
from .models import *
from .serializers import *

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
from django.core import serializers

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

def recommend_exercises(user: User, exercises_to_recommend: int = 1, truly_random = False, bad_recommendation_limit: int = 3, k_neighbours: int = 5):
    exercises: list[RecommendedExercise] = []

    # TODO: implement factors that affect a recommendation e.g. user's daily mood/motivation, etc.
    # TODO: generate points based on given recommendation
    # TODO: handle the case where the user has NO logged exercises and/or NO recommended exercises
    # TODO: handle missing/null values in model

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
                    all_durations: list[timedelta] = list(all_logged_exercises.values_list('duration', flat=True))
                    all_duration_mins = [x.seconds / 60.0 for x in all_durations] if len(all_durations) > 0 else [0]

                    minutes = max(1, round(np.mean(all_duration_mins) * random.uniform(0.8, 1.2), 2))

                    # TODO: generate equipment weight and weight units
                    # TODO: factor in user mood when it comes to the random multiplier at the end
                    # TODO: don't include any if there isn't any data for the logged exercises
                    # TODO: add distance units
                    recommended_exercise.sets = max(1, round((all_logged_exercises.aggregate(Avg("sets", default=1))["sets__avg"]) * random.uniform(0.8, 1.2)))
                    recommended_exercise.reps = max(1, round((all_logged_exercises.filter(sets__gte=recommended_exercise.sets-1).aggregate(Avg("reps", default=1))["reps__avg"]) * random.uniform(0.9, 1.2)))
                    recommended_exercise.distance = max(1, round((all_logged_exercises.aggregate(Avg("distance", default=1))["distance__avg"]) * random.uniform(0.7, 1.3)))
                    recommended_exercise.duration = timedelta(hours=minutes//60, minutes=floor(minutes%60), seconds=((minutes % 1) * 60) // 1)

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
                return api_error("Inavlid Muscle Type")

        # validates exercise type input
        if ex_type not in self.exercise_type:
            return api_error("Invalid Exercise Type")

        # validates body area input
        if ex_body_area not in self.body_area_types:
            return api_error("Inavlid Body Area Type")
        
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
        for attribute in request.data.keys():
            if attribute not in all_exercise_fields:
                return api_error("Unexpected filter name encountered.")
            
        # makes appropriate filters based on exercise attributes
        for attribute in all_exercise_fields:
            if attribute in request.data.keys():
                match(attribute):
                    case "ex_name": query_set = query_set.filter(ex_name=request.data[attribute])
                    case "ex_type": query_set = query_set.filter(ex_type=request.data[attribute])
                    case "ex_body_area": query_set = query_set.filter(ex_body_area=request.data[attribute])
                    case "equipment_needed": query_set = query_set.filter(equipment_needed=request.data[attribute])
                    case "ex_target_muscle": query_set = query_set.filter(ex_target_muscle=request.data[attribute])
                    case _:
                        return api_error("Attribute not accounted for in filter.")

        # return filtered queryset
        return JsonResponse(list(query_set), safe=False)
    
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

        # if equipment_weight is present, should also have units
        if logged_exercise.equipment_weight and not logged_exercise.equipment_weight_units:
            return api_error("Weights used need unit(s).")

        # validates inputs for logged exercise and saves if valid
        if logged_exercise.date_logged is None:
            return api_error("A date for the exercise log must be provided.")

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
            if attribute in request.data.keys():
                match(attribute):
                    case "username": query_set = query_set.filter(user=User.objects.get(username=request.data["username"]))
                    case "email": query_set = query_set.filter(user=User.objects.get(email=request.data["email"]))
                    case "ex_name": query_set = query_set.filter(exercise=Exercise.objects.get(ex_name=request.data["ex_name"]))
                    case "date_logged": query_set = query_set.filter(date_logged=request.data["date_logged"])
                    case "time_logged": query_set = query_set.filter(time_logged=request.data["time_logged"])
                    case "sets": query_set = query_set.filter(sets=request.data["sets"])
                    case "reps": query_set = query_set.filter(reps=request.data["reps"])
                    case "distance": query_set = query_set.filter(distance=request.data["distance"])
                    case "distance_units": query_set = query_set.filter(distance_units=request.data["distance_units"])
                    case "duration": query_set = query_set.filter(duration=request.data["duration"])
                    case "equipment_weight": query_set = query_set.filter(equipment_weight=request.data["equipment_weight"])
                    case "equipment_weight_units": query_set = query_set.filter(equipment_weight_units=request.data["equipment_weight_units"])
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
    serializer_class = LoggedExerciseSerializer

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

        if type(target_user) == Response: return target_user

        # sets the truly_random variable if it is present in the request
        if request.query_params.get("truly_random"):
            try:
                truly_random = request.query_params["truly_random"]
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
            
        # sets the k_neighbours variable if it is present in the request
        if request.query_params.get("k_neighbours"):
            try:
                k_neighbours = request.query_params["k_neighbours"]
                if k_neighbours < 1: return api_error("k_neighbours must be at least 1.")
            except TypeError:
                return api_error("k_neighbours must be an integer.")
            
        return recommend_exercises(user=target_user, exercises_to_recommend=exercises_to_recommend, truly_random=truly_random, k_neighbours=k_neighbours)