from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

macro_keys = [
    "fat_g",
    "saturates_g",
    "trans_fat_g",
    "protein_g",
    "salt_g",
    "fiber_g",
    "carbohydrates_g",
    "sugars_g",
    "cholesterol_g",
]

def positive_validator(value, include_equal: bool = False):
    return value > 0.0 if not include_equal else value >= 0.0

def validate_macros(value):
    if type(value) != dict: return False

    for key in value.keys():
        amount = value[key]
        if key in macro_keys:
            if not positive_validator(amount, include_equal=True):
                return False

    return True


# Defines models and fields
class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    otp = models.CharField(max_length=6, default="", null=False, db_comment="The OTP sent to the user.")
    created_at = models.DateTimeField(auto_now=True, db_comment="When the OTP was created. Useful for restricting the frequency of new OTP generation.")
    expiry_time = models.DateTimeField(db_comment="When the OTP can no longer be accepted. Default is 5 minutes after when it was created.")
    verified = models.BooleanField(default=False, db_comment="Whether the OTP for the user has been verified. Good for preventing repeat entries and also ensuring user is secure.")

class Exercise(models.Model):  
    ex_name = models.CharField(max_length=80, default="", null=False, db_comment="The name of the exercise")
    ex_type = models.CharField(max_length=100, default="", null=False, db_comment="Type of exercise, Cardio, Muscle etc")
    ex_body_area = models.CharField(max_length=15, default="", null=False, db_comment="What body part the exercise is working on: Legs, back, chest etc")
    equipment_needed = models.CharField(max_length=80, default="none", null=False, db_comment="Equipment needed for exercise")
    ex_target_muscle = models.CharField(max_length=20, default="", null=True, db_comment="Target Muscle - can be null for cardio")
    ex_secondary_muscle_1 = models.CharField(max_length=30, default="", null=True, db_comment= "Secondary muscle targeted")
    ex_secondary_muscle_2 = models.CharField(max_length=30, default="", null=True, db_comment="Other Secondary Muscle Targeted")

# TODO: sort the __todict__ function to return None if applicable
# subject to change with extra fields
class LoggedExercise(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, null=False)
    date_logged = models.DateField(default=timezone.now)
    time_logged = models.TimeField(default=timezone.now, null=True)
    sets = models.PositiveSmallIntegerField(default=0, null=True)
    reps = models.PositiveSmallIntegerField(default=0, null=True)
    distance = models.FloatField(default=0.0, null=True)
    distance_units = models.CharField(max_length=5, choices=[("km", "km"), ("mi", "mi")], null=True)
    duration = models.DurationField(default=timedelta(hours=0, minutes=0, seconds=0), null=True)
    equipment_weight = models.JSONField(default=list, null=True) # a list of integers for varying weights if multiple were used, MUST ALWAYS BE A LIST OTHERWISE IT BREAKS
    equipment_weight_units = models.CharField(max_length=2, choices=[("kg", "kg"), ("lb", "lb")], null=True)

    # only for making the ML model easier to import
    # only returns the minimum data necessary
    def __todict__(self):
        return {
            "sets": self.sets if self.sets else 0,
            "reps": self.reps if self.reps else 0,
            "distance": self.distance if self.distance else 0.0,
            "duration_mins": self.duration.seconds / 60.0 if self.duration else 0.0,
            "good": 1, # since it's been logged its obviously a good exercise (?)
        }

# whether a user is verified or not
class VerifiedUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    verified = models.BooleanField(default=False)

# TODO: sort the __todict__ function to return None if applicable
class RecommendedExercise(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    datetime_recommended = models.DateTimeField(default=timezone.now)
    good_recommendation = models.BooleanField(default=True)
    sets = models.PositiveSmallIntegerField(default=0, null=True)
    reps = models.PositiveSmallIntegerField(default=0, null=True)
    distance = models.FloatField(default=0.0, null=True)
    distance_units = models.CharField(max_length=5, choices=[("km", "km"), ("mi", "mi")], null=True)
    duration = models.DurationField(default=timedelta(hours=0, minutes=0, seconds=0), null=True)
    equipment_weight = models.JSONField(default=list, null=True) # a list of integers for varying weights if multiple were used
    equipment_weight_units = models.CharField(max_length=2, choices=[("kg", "kg"), ("lb", "lb")], null=True)

    # only for making the ML model easier to import
    # only returns the minimum data necessary
    def __todict__(self):
        return {
            "sets": self.sets if self.sets else 0,
            "reps": self.reps if self.reps else 0,
            "distance": self.distance if self.distance else 0.0,
            "duration_mins": self.duration.seconds / 60.0,
            "good": 1 if self.good_recommendation else 0,
        }
class UserData(models.Model):
    SEX_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('X', 'Prefer not to say/Other'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # User is a foreign key, not null
    user_age = models.PositiveSmallIntegerField()  # Positive int (must be >= 0)
    user_sex = models.CharField(max_length=1, choices=SEX_CHOICES, null=True, blank=True)
    user_height = models.FloatField()  
    user_height_units = models.CharField(max_length=2, choices=[('in', 'Inches'), ('cm', 'Centimeters')]) 
    user_weight = models.FloatField(null=True)  
    user_weight_units = models.CharField(max_length=2, choices=[('lb', 'Pounds'), ('kg', 'Kilograms')], null=True)
    
    def __str__(self):
        return f"User Data for {self.user.username}"
    
# this took a LOT of thinking to make but for simplicity of implementation, we are keeping it as so for now
# i tried thinking about how to make it from other consumables but it broke my brain
class Consumable(models.Model):
    global macro_keys, positive_validator, validate_macros

    name = models.CharField(max_length=50, primary_key=True, unique=True) # primary key because it's unique. also stops consumable logging
    sample_size = models.FloatField(validators=[positive_validator])
    sample_units = models.CharField(max_length=20, default="serving")
    sample_calories = models.PositiveIntegerField()
    sample_macros = models.JSONField(validators=[validate_macros], null=True)
    logged_user = models.ManyToManyField(to=User, through="LoggedConsumable")

class LoggedConsumable(models.Model):
    global macro_keys, positive_validator, validate_macros

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    consumable = models.ForeignKey(Consumable, on_delete=models.DO_NOTHING) # do nothing does create integrity issues, however PK is a string and so is still useable for now-deleted consumables (should never happen but edge case is accounted for)
    amount_logged = models.FloatField(validators=[positive_validator]) # this is a multiplier based on the sample_size of the Consumable
    date_logged = models.DateField() # this is NOT when the instance was created, but when the consumable was consumed.
    calories_logged = models.PositiveIntegerField()
    macros_logged = models.JSONField(validators=[validate_macros], null=True)

class UserMood(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mood_level = models.SmallIntegerField(default=0)
    datetime_recorded = models.DateTimeField(default=timezone.now)
