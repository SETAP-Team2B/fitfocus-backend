from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

# Create your models here.
class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    otp = models.CharField(max_length=6, default="", null=False, db_comment="The OTP sent to the user.")
    created_at = models.DateTimeField(auto_now=True, db_comment="When the OTP was created. Useful for restricting the frequency of new OTP generation.")
    expiry_time = models.DateTimeField(default=timezone.now() + timezone.timedelta(minutes=5), db_comment="When the OTP can no longer be accepted. Default is 5 minutes after when it was created.")
    verified = models.BooleanField(default=False, db_comment="Whether the OTP for the user has been verified. Good for preventing repeat entries and also ensuring user is secure.")

class Exercise(models.Model):  
    ex_name = models.CharField(max_length=80, default="", null=False, db_comment="The name of the exercise")
    ex_type = models.CharField(max_length=100, default="", null=False, db_comment="Type of exercise, Cardio, Muscle etc")
    ex_body_area = models.CharField(max_length=15, default="", null=False, db_comment="What body part the exercise is working on: Legs, back, chest etc")
    equipment_needed = models.CharField(max_length=80, default="none", null=False, db_comment="Equipment needed for exercise")
    ex_target_muscle = models.CharField(max_length=20, default="", null=True, db_comment="Target Muscle - can be null for cardio")
    ex_secondary_muscle = models.CharField(max_length=30, default="", null=True, db_comment= "Secondary muscle targeted")

# subject to change with extra fields
class LoggedExercise(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, null=False)
    date_logged = models.DateField(default=timezone.now().date(), null=False)
    time_logged = models.TimeField(default=timezone.now().time())
    sets = models.PositiveSmallIntegerField(default=0)
    reps = models.PositiveSmallIntegerField(default=0)
    distance = models.FloatField(default=0.0)
    distance_units = models.CharField(max_length=5, choices=[("km", "km"), ("mi", "mi")])
    duration = models.DurationField(default=timedelta(hours=0, minutes=0, seconds=0))
    equipment_weight = models.JSONField(default=list) # a list of integers for varying weights if multiple were used
    equipment_weight_units = models.CharField(max_length=2, choices=[("kg", "kg"), ("lb", "lb")])